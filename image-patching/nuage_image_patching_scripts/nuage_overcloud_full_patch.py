# !/usr/bin/python3
# Copyright 2020 NOKIA
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an
#    "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
#    either express or implied. See the License for the specific
#    language governing permissions and limitations under the License.

import argparse
import yaml
import sys
import logging
from nuage_image_patching_scripts.utils import constants as constants
from nuage_image_patching_scripts.utils.common import *

'''
This script is used to patch an existing OpenStack
image with Nuage components
This script takes in following input parameters:
 RhelUserName      : User name for the RHEL subscription
 RhelPassword      : Password for the RHEL subscription
 RhelPool          : RHEL Pool to subscribe
 RhelSatUrl        : RHEL Satellite url
 RhelSatOrg        : RHEL Satellite organisation
 RhelSatActKey     : RHEL Satellite activation key
 RepoFile          : Name for the file repo hosting the Nuage RPMs
 DeploymentType    : ["avrs"] --> AVRS + VRS/OVRS/SRIOV deployment
                     ["vrs"]  --> VRS/OVRS/SRIOV deployment
 VRSRepoNames      : Name for the repo hosting the Nuage O/VRS RPMs
 RpmPublicKey      : RPM GPG Key
 logFile           : Log file name

The following sequence is executed by the script
 1. Subscribe to RHEL and the pool
 2. Uninstall OVS
 3. Download AVRS packages to the image if AVRS is enabled
 4. Install NeutronClient, Nuage-BGP, Selinux Policy Nuage,
    Nuage Puppet Module packages.
 5. Install VRS, Nuage Metadata Agent
 6. Unsubscribe from RHEL
'''

logger = logging.getLogger(constants.LOG_FILE_NAME)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
rhel_subs_type = ''


#####
# Function to install Nuage packages that are required
#####

def install_nuage_packages():
    cmds = '''
#### Installing Nuage Packages
yum install --setopt=skip_missing_names_on_install=False -y %s
yum install --setopt=skip_missing_names_on_install=False -y %s
yum install --setopt=skip_missing_names_on_install=False -y %s
yum clean all
''' % (constants.NUAGE_DEPENDENCIES, constants.NUAGE_VRS_PACKAGE,
       constants.NUAGE_PACKAGES)
    constants.PATCHING_SCRIPT += cmds + '\n'


#####
# Function to download Nuage AVRS packages that are required
#####

def download_avrs_packages():
    cmds = '''
#### Downloading Nuage Avrs and 6wind Packages
yum install -y yum-utils
mkdir -p /6wind
rpm -q kernel | awk '{ print substr($1,8) }' > /kernel-version
yumdownloader -y --setopt=skip_missing_names_on_install=False \
--downloadonly --downloaddir=/6wind *6windgate* iptables*6windgate* \
ebtables*6windgate*
yumdownloader -y --setopt=skip_missing_names_on_install=False \
--downloadonly --downloaddir=/6wind python3-pyelftools* \
%s nuage-metadata-agent virtual-accelerator*
yumdownloader -y --setopt=skip_missing_names_on_install=False \
--downloadonly --downloaddir=/6wind selinux-policy-nuage-avrs*
yumdownloader -y --setopt=skip_missing_names_on_install=False \
--downloadonly --downloaddir=/6wind python3-pyroute2

yum install --setopt=skip_missing_names_on_install=False -y createrepo
yum clean all
''' % constants.NUAGE_AVRS_PACKAGE
    constants.PATCHING_SCRIPT += cmds + '\n'


#####
# Function to check if deployment types provided are valid
#####

def check_deployment_type(nuage_config):
    msg = "DeploymentType config option %s is not correct " \
          "or supported " \
          " Please enter:\n ['vrs'] --> for VRS/OVRS/SRIOV deployment\n " \
          "['avrs'] --> for AVRS + VRS/OVRS/SRIOV deployment\n " % \
          nuage_config["DeploymentType"]
    if (all(deployment_type in constants.VALID_DEPLOYMENT_TYPES
            for deployment_type in nuage_config["DeploymentType"])):
        logger.info("Overcloud Image will be patched with Nuage %s "
                    "rpms" % nuage_config["DeploymentType"])
    else:
        logger.error(msg)
        sys.exit(1)


def check_rhel_subscription_type(nuage_config):
    """
    Check which type of red hat subscription to use
    """
    key_set_satellite = ["RhelSatUrl", "RhelSatOrg", "RhelSatActKey"]
    key_set_portal = ["RhelPassword", "RhelUserName", "RhelPool"]

    if all(nuage_config.get(key) for key in
           key_set_satellite):  # RH satellite
        return constants.RHEL_SUB_SATELLITE
    elif all(nuage_config.get(key) for key in
             key_set_portal):  # RH portal
        return constants.RHEL_SUB_PORTAL
    elif all(not nuage_config.get(key) for key in
             key_set_portal + key_set_satellite):  # RH disabled
        return constants.RHEL_SUB_DISABLED
    else:  # RH incomplete configuration
        logger.error(
            'INCOMPLETE Red Hat subscription configuration detected: \n'
            '   - For Red Hat Portal please specify: '
            '[RhelPassword, RhelUserName, RhelPool] \n'
            '   - For Red Hat Satellite please specify: '
            '[RhelUrl, RhelSatOrg, RhelSatActKey]')
        sys.exit(1)


def check_config(nuage_config):
    global rhel_subs_type
    logger.info("Verifying pre-requisite packages for script")
    libguestfs = cmds_run(['rpm -q libguestfs-tools-c'])
    if 'not installed' in libguestfs:
        logger.info("Please install libguestfs-tools-c package "
                    "for the script to run")
        sys.exit(1)

    rhel_subs_type = check_rhel_subscription_type(nuage_config)

    if not nuage_config.get("ImageName"):
        logger.error("Please provide missing config %s value "
                     "in your config file. \n" % "ImageName")
        sys.exit(1)

    if not nuage_config.get(
            "RepoFile") and not rhel_subs_type == constants.RHEL_SUB_SATELLITE:
        logger.error("Please provide missing config %s value "
                     "in your config file. \n" % "RepoFile")
        sys.exit(1)

    file_exists(nuage_config["ImageName"])

    check_deployment_type(nuage_config)


####
# Image Patching
####


def image_patching(nuage_config):
    global rhel_subs_type
    start_script()

    if nuage_config.get("RpmPublicKey"):
        logger.info("Importing gpgkey(s) to overcloud image")
        importing_gpgkeys(nuage_config["ImageName"],
                          nuage_config["RpmPublicKey"])

    if (rhel_subs_type == constants.RHEL_SUB_PORTAL
            or rhel_subs_type == constants.RHEL_SUB_SATELLITE):
        rhel_subscription(username=nuage_config.get("RhelUserName"),
                          password=nuage_config.get("RhelPassword"),
                          pool=nuage_config.get("RhelPool"),
                          satellite_url=nuage_config.get("RhelSatUrl"),
                          satellite_org=nuage_config.get("RhelSatOrg"),
                          satellite_key=nuage_config.get("RhelSatActKey"),
                          proxy_hostname=nuage_config.get("ProxyHostname"),
                          proxy_port=nuage_config.get("ProxyPort"),
                          rhel_sub_type=rhel_subs_type,
                          deployment_type=nuage_config.get("DeploymentType"))
    install_nuage_python_ovs_packages()
    uninstall_packages()

    if nuage_config.get("RepoFile"):
        # If: RH satellite
        #   - Add nuage packages to the RH satellite
        #   - Use RepoFile for nuage packages, RH satellite for RH packages
        # Else: check_config checks if file is missing
        logger.info("Copying RepoFile to the overcloud image")
        copy_repo_file(nuage_config["ImageName"], nuage_config["RepoFile"])

    if "avrs" in nuage_config["DeploymentType"]:
        download_avrs_packages()

    install_nuage_packages()

    if (rhel_subs_type == constants.RHEL_SUB_PORTAL
            or rhel_subs_type == constants.RHEL_SUB_SATELLITE):
        rhel_remove_subscription(rhel_sub_type=rhel_subs_type)

    write_to_file(constants.PATCHING_SCRIPT)
    logger.info("Running the patching script on Overcloud image")

    virt_customize_run(
        ' %s -a %s --memsize %s --selinux-relabel' % (
            constants.SCRIPT_NAME, nuage_config["ImageName"],
            constants.VIRT_CUSTOMIZE_MEMSIZE))

    logger.info("Reset the Machine ID")
    cmds_run([constants.VIRT_CUSTOMIZE_ENV + "virt-sysprep --operation "
                                             "machine-id -a %s" %
              nuage_config["ImageName"]])
    logger.info("Done")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nuage-config", dest="nuage_config",
                        required=True,
                        help="path to nuage_patching_config.yaml")
    args = parser.parse_args()

    with open(args.nuage_config) as nuage_config:
        try:
            nuage_config = yaml.load(nuage_config)
        except yaml.YAMLError as exc:
            logger.error(
                'Error parsing file {filename}: {exc}. \n'
                'Please fix and try again with correct yaml file.'
                    .format(filename=args.nuage_config, exc=exc))
            sys.exit(1)

    if nuage_config.get("logFileName"):
        handler = logging.FileHandler(nuage_config["logFileName"])
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.info("nuage_overcloud_full_patch.py was "
                "run with following config options %s " % nuage_config)
    check_config(nuage_config)
    image_patching(nuage_config)


if __name__ == "__main__":
    main()
