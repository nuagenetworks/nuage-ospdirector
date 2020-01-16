# !/usr/bin/python
# Copyright 2019 NOKIA
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
import utils.constants as constants
from utils.common import *

'''
This script is used to patch an existing OpenStack
image with Nuage components
This script takes in following input parameters:
 RhelUserName      : User name for the RHEL subscription
 RhelPassword      : Password for the RHEL subscription
 RhelPool          : RHEL Pool to subscribe
 RepoFile          : Name for the file repo hosting the Nuage RPMs
 DeploymentType    : ["ovrs"] --> OVRS deployment
                     ["avrs"] --> AVRS + VRS deployment
                     ["vrs"]  --> VRS deployment
 VRSRepoNames      : Name for the repo hosting the Nuage O/VRS RPMs 
 AVRSRepoNames     : Name for the repo hosting the Nuage AVRS RPMs
 OvrsRepoNames : Name for the repo hosting the Mellanox RPMs
 KernelRepoNames   : Name for the repo hosting the Kernel RPMs
 RpmPublicKey      : RPM GPG Key 
 logFile           : Log file name
The following sequence is executed by the script
 1. Subscribe to RHEL and the pool
 2. Uninstall OVS
 3. Download AVRS packages to the image if AVRS is enabled
 4. Install NeutronClient, Nuage-BGP, Selinux Policy Nuage, 
    Nuage Puppet Module, Redhat HF and Mellanox packages.
 5. Install O/VRS, Nuage Metadata Agent
 6. Unsubscribe from RHEL
'''

logger = logging.getLogger(constants.LOG_FILE_NAME)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

#####
# Decorator function to enable and disable repos for
# NuageMajorVersion "5.0" and skip it for "6.0"
#####


def repos_decorator(func):
    def repos_wrapper(version, reponames):
        install_cmds = func()
        if version == "5.0":
            enable_repos_cmd = "yum-config-manager --enable"
            for repo in reponames:
                enable_repos_cmd += " %s" % repo
            disable_repos_cmd = enable_repos_cmd.replace("enable",
                                                         "disable")
            full_cmds = enable_repos_cmd + install_cmds + \
                        disable_repos_cmd
        else:
            full_cmds = install_cmds
        write_to_file(constants.SCRIPT_NAME, full_cmds)
        write_to_file(constants.SCRIPT_NAME, '\n')
    return repos_wrapper


#####
# Function to install Nuage packages that are required
#####

@repos_decorator
def install_nuage_packages():

    cmds = '''
#### Installing Nuage Packages
yum install --setopt=skip_missing_names_on_install=False -y %s
yum install --setopt=skip_missing_names_on_install=False -y %s
yum install --setopt=skip_missing_names_on_install=False -y %s
yum clean all
''' % (constants.NUAGE_DEPENDENCIES, constants.NUAGE_VRS_PACKAGE,
       constants.NUAGE_PACKAGES)
    return cmds

#####
# Function to install Mellanox packages that are required
#####


@repos_decorator
def install_mellanox():

    cmds = '''
#### Installing Mellanox OFED and os-net-config Packages
yum install --setopt=skip_missing_names_on_install=False -y %s
yum clean all
''' % constants.MLNX_OFED_PACKAGES
    return cmds


#####
# Updating kernel to Red Hat Hot Fix
#####

@repos_decorator
def update_kernel():

    cmds = '''
#### Installing Kernel Hot Fix Packages
yum install --setopt=skip_missing_names_on_install=False -y %s
yum clean all
''' % constants.KERNEL_PACKAGES
    return cmds


#####
# Function to download Nuage AVRS packages that are required
#####

@repos_decorator
def download_avrs_packages():

    cmds = '''
#### Downloading Nuage Avrs and 6wind Packages
mkdir -p /6wind
touch /kernel-version
rpm -q kernel | awk '{ print substr($1,8) }' > /kernel-version
yum install --setopt=skip_missing_names_on_install=False \
--downloadonly --downloaddir=/6wind \
kernel-headers-$(awk 'END{print}' /kernel-version) \
kernel-devel-$(awk 'END{print}' /kernel-version) python-pyelftools* \
dkms* 6windgate* %s nuage-metadata-agent virtual-accelerator*
yum install --setopt=skip_missing_names_on_install=False \
--downloadonly --downloaddir=/6wind selinux-policy-nuage-avrs*
yum install --setopt=skip_missing_names_on_install=False \
--downloadonly --downloaddir=/6wind 6wind-openstack-extensions
rm -rf /kernel-version
yum clean all
''' % constants.NUAGE_AVRS_PACKAGE
    return cmds


#####
# Function to download Nuage OVRS package
#####


@repos_decorator
def download_ovrs_package():
    cmds = '''
#### Downloading Nuage Ovrs Package
mkdir -p /ovrs
yum install --setopt=skip_missing_names_on_install=False \
 --downloadonly  --downloaddir=/ovrs nuage-openvswitch-ovrs \
nuage-metadata-agent
yum clean all
'''
    return cmds


#####
# Function to check the repo names are provided for 5.0
#####


def check_reponames(nuage_config):
    if "vrs" in nuage_config["DeploymentType"]:
        if not nuage_config.get("VRSRepoNames"):
            logger.error("Please provide AVRSRepoNames "
                         "for AVRS deployment")
            sys.exit(1)
    elif "avrs" in nuage_config["DeploymentType"]:
        if not nuage_config.get("VRSRepoNames"):
            logger.error("Please provide VRSRepoNames "
                         "for AVRS deployment")
            sys.exit(1)
        if not nuage_config.get("AVRSRepoNames"):
            logger.error("Please provide AVRSRepoNames "
                         "for AVRS deployment")
            sys.exit(1)
    elif "ovrs" in nuage_config["DeploymentType"]:
        if not nuage_config.get("OvrsRepoNames"):
            logger.error(
                "Please provide OvrsRepoNames for OVRS deployment")
            sys.exit(1)
    else:
        logger.error("DeploymentType config option %s is not correct "
                     "or supported "
                     " Please enter:\n ['vrs'] --> for VRS "
                     "deployment\n "
                     "['avrs'] --> for AVRS + VRS deployment\n "
                     "['ovrs'] --> for OVRS deployment"
                     % nuage_config["DeploymentType"])
        sys.exit(1)

    if nuage_config.get("KernelHF"):
        if not nuage_config.get("KernelRepoNames"):
            logger.error(
                "Please provide KernelRepoNames for Kernel Hot Fix")
            sys.exit(1)


#####
# Function to check if deployment types provided are valid
#####

def check_deployment_type(nuage_config):
    msg = "DeploymentType config option %s is not correct " \
          "or supported " \
          " Please enter:\n ['vrs'] --> for VRS deployment\n " \
          "['avrs'] --> for AVRS + VRS deployment\n " \
          "['ovrs'] --> for OVRS deployment" % \
          nuage_config["DeploymentType"]
    if(all(deployment_type in constants.VALID_DEPLOYMENT_TYPES
           for deployment_type in nuage_config["DeploymentType"])):
        logger.info("Overcloud Image will be patched with Nuage %s "
                    "rpms" % nuage_config["DeploymentType"])
    else:
        logger.error(msg)
        sys.exit(1)


def check_config(nuage_config):
    logger.info("Verifying pre-requisite packages for script")
    libguestfs = cmds_run(['rpm -q libguestfs-tools-c'])
    if 'not installed' in libguestfs:
        logger.info("Please install libguestfs-tools-c package "
                    "for the script to run")
        sys.exit(1)

    if not nuage_config["NuageMajorVersion"] in ["5.0", "6.0"]:
        logger.error("NuageMajorVersion %s is not valid"
                     "Available options are either '5.0 or '6.0' "
                     % nuage_config["NuageMajorVersion"])
        sys.exit(1)
    missing_config = []
    for key in ["ImageName", "RepoFile"]:
        if not (nuage_config.get(key)):
            missing_config.append(key)
    if missing_config:
        logger.error("Please provide missing config %s value "
                     "in your config file. \n" % missing_config)
        sys.exit(1)
    file_exists(nuage_config["ImageName"])

    check_deployment_type(nuage_config)
    if nuage_config["NuageMajorVersion"] == "5.0":
        check_reponames(nuage_config)
        constants.NUAGE_AVRS_PACKAGE = "nuage-openvswitch"
        constants.MLNX_OFED_PACKAGES = "kmod-mlnx-en mlnx-en-utils " \
                                       "mstflint os-net-config"

####
# Image Patching
####


def image_patching(nuage_config):

    start_script()

    if nuage_config.get("RpmPublicKey"):
        logger.info("Importing gpgkey(s) to overcloud image")
        importing_gpgkeys(nuage_config["ImageName"],
                          nuage_config["RpmPublicKey"])

    if nuage_config.get("RhelUserName") and nuage_config.get(
            "RhelPassword") and nuage_config.get("RhelPool"):
        if nuage_config.get("ProxyHostname") and \
                nuage_config.get("ProxyPort"):
            rhel_subscription(
                nuage_config["RhelUserName"],
                nuage_config["RhelPassword"],
                nuage_config["RhelPool"],
                nuage_config["ProxyHostname"],
                nuage_config["ProxyPort"])
        else:
            rhel_subscription(
                nuage_config["RhelUserName"],
                nuage_config["RhelPassword"],
                nuage_config["RhelPool"])
    install_nuage_python_ovs_packages()
    uninstall_packages()

    logger.info("Copying RepoFile to the overcloud image")
    copy_repo_file(nuage_config["ImageName"], nuage_config["RepoFile"])

    if nuage_config['KernelHF']:
        update_kernel(nuage_config["NuageMajorVersion"], nuage_config[
            "KernelRepoNames"])

    if "ovrs" in nuage_config["DeploymentType"]:
        download_ovrs_package(nuage_config["NuageMajorVersion"],
                              nuage_config["OvrsRepoNames"])
        install_mellanox(nuage_config["NuageMajorVersion"],
                         nuage_config["OvrsRepoNames"])

    if "avrs" in nuage_config["DeploymentType"]:
        download_avrs_packages(nuage_config["NuageMajorVersion"],
                               nuage_config["AVRSRepoNames"])

    install_nuage_packages(nuage_config["NuageMajorVersion"],
                           nuage_config["VRSRepoNames"])

    if nuage_config.get("RhelUserName") and nuage_config.get(
            "RhelPassword") and nuage_config.get("RhelPool"):
        rhel_remove_subscription()

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
    logger.info("nuage_overcloud_full_patch.py was "
                "run with following config options %s " % nuage_config)
    check_config(nuage_config)
    image_patching(nuage_config)


if __name__ == "__main__":
    main()
