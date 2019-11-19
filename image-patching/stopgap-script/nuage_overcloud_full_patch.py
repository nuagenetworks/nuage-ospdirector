# !/usr/bin/python
# Copyright 2019 NOKIA
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import subprocess
import sys
import logging
import os
import yaml

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
 MellanoxRepoNames : Name for the repo hosting the Mellanox RPMs
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

# List of Nuage packages
NUAGE_PACKAGES = "nuage-puppet-modules selinux-policy-nuage " \
                 "nuage-bgp nuage-openstack-neutronclient"
NUAGE_DEPENDENCIES = "libvirt perl-JSON lldpad"
NUAGE_VRS_PACKAGE = "nuage-openvswitch nuage-metadata-agent"
MLNX_OFED_PACKAGES = "mstflint"
KERNEL_PACKAGES = "kernel kernel-tools kernel-tools-libs python-perf"
VIRT_CUSTOMIZE_MEMSIZE = "2048"
VIRT_CUSTOMIZE_ENV = "export LIBGUESTFS_BACKEND=direct;"
SCRIPT_NAME = 'patching_script.sh'
GPGKEYS_PATH = '/tmp/'

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


#####
# Function to run commands on the console
#####
# quotes


def cmds_run(cmds):
    if not cmds:
        return
    output_list = []
    for cmd in cmds:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            close_fds=True)
        (out, err) = proc.communicate()
        if err and err.split():
            logger.error(
                "error occurred during command:\n %s\n error:\n %s \n "
                "exiting" % (cmd, err))
            sys.exit(1)
        output_list.append(out)

    if len(cmds) == 1:
        if output_list[0]:
            logger.debug("%s" % output_list[0])
        return output_list[0]
    else:
        if output_list:
            logger.debug("%s" % output_list)
        return output_list


def virt_customize(command):
    return cmds_run(
        [VIRT_CUSTOMIZE_ENV + 'virt-customize --run-command %s' % command])


def virt_customize_run(command):
    return cmds_run([VIRT_CUSTOMIZE_ENV + 'virt-customize --run %s' % command])


def virt_copy(command):
    return cmds_run([VIRT_CUSTOMIZE_ENV + 'virt-copy-in -a %s' % command])


#####
# Check if the provided path to the file exists
#####


def file_exists(filename):
    if os.path.isfile(filename):
        return True
    else:
        logger.error("%s is not present in the location of this "
                     "script" % filename)
        sys.exit(1)


#####
# Function to add RHEL subscription using guestfish
#####


def start_script():
    if os.path.isfile(SCRIPT_NAME):
        os.remove(SCRIPT_NAME)

    cmds = '''#!/bin/bash
set -xe
'''
    write_to_file(SCRIPT_NAME, cmds)


#####
# Function that writes commands to a file
#####

def write_to_file(filename, contents):
    with open(filename, 'a') as script:
        script.writelines(contents)


#####
# Function to add RHEL subscription using guestfish
#####


def rhel_subscription(username,
                      password,
                      pool,
                      proxy_hostname=None,
                      proxy_port=None):
    subscription_command = ''
    if proxy_hostname is not None:
        subscription_command = "subscription-manager config --server.proxy_hostname=%s  --server.proxy_port=%s\n" % (
            proxy_hostname, proxy_port)

    enable_pool = '''
subscription-manager register --username='%s' --password='%s'
subscription-manager attach --pool='%s'
subscription-manager repos --enable=rhel-7-server-optional-rpms
subscription-manager repos --enable=rhel-7-server-rpms
''' % (username, password, pool)
    cmds = subscription_command + enable_pool
    write_to_file(SCRIPT_NAME, cmds)


#####
# Function to remove the RHEL subscription
#####


def rhel_remove_subscription():
    cmd = '''
#### Removing RHEL Subscription
subscription-manager unregister
'''
    write_to_file(SCRIPT_NAME, cmd)


#####
# Function to remove packages that are not needed
#####


def uninstall_packages():
    cmd = '''
#### Removing Upstream OpenvSwitch
yum remove openvswitch -y
'''
    write_to_file(SCRIPT_NAME, cmd)


#####
# Function to install Nuage packages that are required
#####


def install_nuage_packages(nuage_vrs_repos):
    enable_repos_cmd = "yum-config-manager --enable"
    for repo in nuage_vrs_repos:
        enable_repos_cmd += " %s" % (repo)
    disable_repos_cmd = enable_repos_cmd.replace("enable", "disable")

    cmds = '''
#### Installing Nuage Packages
%s
yum install --setopt=skip_missing_names_on_install=False -y %s
yum install --setopt=skip_missing_names_on_install=False -y %s
yum install --setopt=skip_missing_names_on_install=False -y %s
%s
''' % (enable_repos_cmd, NUAGE_DEPENDENCIES, NUAGE_VRS_PACKAGE,
       NUAGE_PACKAGES, disable_repos_cmd)

    write_to_file(SCRIPT_NAME, cmds)


#####
# Function to install Mellanox packages that are required
#####


def install_mellanox(mellanox_repos):
    # Installing Mellanox OFED Packages
    enable_repos_cmd = "yum-config-manager --enable"

    for repo in mellanox_repos:
        enable_repos_cmd += " %s" % (repo)
    disable_repos_cmd = enable_repos_cmd.replace("enable", "disable")
    cmds = '''
#### Installing Mellanox OFED and os-net-config Packages
%s
yum clean all
yum install --setopt=skip_missing_names_on_install=False -y %s
%s
''' % (enable_repos_cmd, MLNX_OFED_PACKAGES, disable_repos_cmd)
    write_to_file(SCRIPT_NAME, cmds)


#####
# Updating kernel to Red Hat Hot Fix
#####


def update_kernel(rh_repos):
    # Updating Kernel
    enable_repos_cmd = "yum-config-manager --enable"
    for repo in rh_repos:
        enable_repos_cmd += " %s" % (repo)
    disable_repos_cmd = enable_repos_cmd.replace("enable", "disable")
    cmds = '''
#### Installing Kernel Hot Fix Packages
%s
yum clean all
yum install --setopt=skip_missing_names_on_install=False -y %s
%s
''' % (enable_repos_cmd, KERNEL_PACKAGES, disable_repos_cmd)
    write_to_file(SCRIPT_NAME, cmds)


#####
# Function to install Nuage AVRS packages that are required
#####


def download_avrs_packages(nuage_avrs_repos):
    enable_repos_cmd = "yum-config-manager --enable"
    for repo in nuage_avrs_repos:
        enable_repos_cmd += " %s" % (repo)
    disable_repos_cmd = enable_repos_cmd.replace("enable", "disable")
    cmds = '''
#### Downloading Nuage Avrs and 6wind Packages
%s
mkdir -p /6wind
rm -rf /var/cache/yum/Nuage
yum clean all
touch /kernel-version
rpm -q kernel | awk '{ print substr($1,8) }' > /kernel-version
yum install --setopt=skip_missing_names_on_install=False -y createrepo
yum install --setopt=skip_missing_names_on_install=False --downloadonly --downloaddir=/6wind kernel-headers-$(awk 'END{print}' /kernel-version) kernel-devel-$(awk 'END{print}' /kernel-version) python-pyelftools* dkms* 6windgate*
yum install --setopt=skip_missing_names_on_install=False --downloadonly --downloaddir=/6wind nuage-openvswitch nuage-metadata-agent
yum install --setopt=skip_missing_names_on_install=False --downloadonly --downloaddir=/6wind virtual-accelerator*
yum install --setopt=skip_missing_names_on_install=False --downloadonly --downloaddir=/6wind selinux-policy-nuage-avrs*
yum install --setopt=skip_missing_names_on_install=False --downloadonly --downloaddir=/6wind 6wind-openstack-extensions
rm -rf /kernel-version
yum clean all
%s
''' % (enable_repos_cmd, disable_repos_cmd)
    write_to_file(SCRIPT_NAME, cmds)


#####
# Importing Gpgkeys to Overcloud image
#####


def importing_gpgkeys(image, gpgkeys):
    cmd = '''
#### Importing GPG keys
'''
    write_to_file(SCRIPT_NAME, cmd)
    for gpgkey in gpgkeys:
        file_exists = os.path.isfile(gpgkey)
        file_name = os.path.basename(gpgkey)
        if file_exists:
            virt_copy('%s %s %s' % (image, gpgkey, GPGKEYS_PATH))
            rpm_import = '''
rpm --import %s%s
''' % (GPGKEYS_PATH, file_name)
            write_to_file(SCRIPT_NAME, rpm_import)

        else:
            logger.error("Nuage package signing key is not present in %s ,"
                         "Installation cannot proceed.  Please place the "
                         "signing key in the correct location and retry" %
                         gpgkey)

            sys.exit(1)


####
# Copying repo file to overcloud image
####


def copy_repo_file(image, repofile):
    if os.path.isfile(repofile):
        virt_copy('%s %s /etc/yum.repos.d/' % (image, repofile))
    else:
        logger.error("Repo file doesn't exists at %s"
                     "Please provide the correct path of RepoFile" %
                     repofile)
        sys.exit(1)


####
# Image Patching
####


def image_patching(nuage_config):
    if nuage_config.get("logFileName"):
        handler = logging.FileHandler(nuage_config["logFileName"])
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    start_script()

    if nuage_config.get("RpmPublicKey"):
        logger.info("Importing gpgkey(s) to overcloud image")
        importing_gpgkeys(nuage_config["ImageName"],
                          nuage_config["RpmPublicKey"])

    if nuage_config.get("RhelUserName") and nuage_config.get(
            "RhelPassword") and nuage_config.get("RhelPool"):
        if nuage_config.get("ProxyHostname") and nuage_config.get("ProxyPort"):
            rhel_subscription(
                nuage_config["RhelUserName"], nuage_config["RhelPassword"],
                nuage_config["RhelPool"], nuage_config["ProxyHostname"],
                nuage_config["ProxyPort"])
        else:
            rhel_subscription(
                nuage_config["RhelUserName"], nuage_config["RhelPassword"],
                nuage_config["RhelPool"])
    uninstall_packages()

    logger.info("Copying RepoFile to the overcloud image")
    copy_repo_file(nuage_config["ImageName"], nuage_config["RepoFile"])

    if nuage_config['KernelHF']:
        update_kernel(nuage_config["KernelRepoNames"])

    if "ovrs" in nuage_config["DeploymentType"]:
        install_mellanox(nuage_config["MellanoxRepoNames"])

    if "avrs" in nuage_config["DeploymentType"]:
        download_avrs_packages(nuage_config["AVRSRepoNames"])

    install_nuage_packages(nuage_config["VRSRepoNames"])

    if nuage_config.get("RhelUserName") and nuage_config.get(
            "RhelPassword") and nuage_config.get("RhelPool"):
        rhel_remove_subscription()

    logger.info("Running the patching script on Overcloud image")
    virt_customize_run(
        ' %s -a %s --memsize %s --selinux-relabel' % (
            SCRIPT_NAME, nuage_config["ImageName"],
            VIRT_CUSTOMIZE_MEMSIZE))
    logger.info("Reset the Machine ID")
    cmds_run([VIRT_CUSTOMIZE_ENV + "virt-sysprep --operation machine-id -a %s" % nuage_config["ImageName"]])
    logger.info("Done")


def check_config(nuage_config):
    missing_config = []
    for key in ["ImageName", "RepoFile", "VRSRepoNames"]:
        if not (nuage_config.get(key)):
            missing_config.append(key)
    if missing_config:
        logger.error("Please provide missing config %s value "
                     "in your config file. \n" % missing_config)
        sys.exit(1)
    file_exists(nuage_config["ImageName"])
    if nuage_config.get("KernelHF"):
        if not nuage_config.get("KernelRepoNames"):
            logger.error(
                "Please provide KernelRepoNames for Kernel Hot Fix")
            sys.exit(1)
    msg = "DeploymentType config option %s is not correct or supported " \
          " Please enter:\n ['vrs'] --> for VRS deployment\n " \
          "['avrs'] --> for AVRS + VRS deployment\n " \
          "['ovrs'] --> for OVRS deployment" % nuage_config["DeploymentType"]
    if len(nuage_config["DeploymentType"]) > 1:
        new_msg = "Multiple " + msg
        logger.error(new_msg)
        sys.exit(1)
    elif "vrs" in nuage_config["DeploymentType"]:
        logger.info("Overcloud Image will be patched with Nuage VRS rpms")
    elif "avrs" in nuage_config["DeploymentType"]:
        logger.info("Overcloud Image will be patched with Nuage VRS & AVRS rpms")
        if not nuage_config.get("AVRSRepoNames"):
            logger.error("Please provide AVRSRepoNames for AVRS deployment")
            sys.exit(1)
    elif  "ovrs" in nuage_config["DeploymentType"]:
        logger.info("Overcloud Image will be patched with OVRS rpms")
        if not nuage_config.get("MellanoxRepoNames"):
            logger.error(
                "Please provide MellanoxRepoNames for OVRS deployment")
            sys.exit(1)
    else:
        logger.error(msg)
        sys.exit(1)
    logger.info("Verifying pre-requisite packages for script")
    libguestfs = cmds_run(['rpm -q libguestfs-tools-c'])
    if 'not installed' in libguestfs:
        logger.info("Please install libguestfs-tools-c package for the script to run")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--nuage-config",
        dest="nuage_config",
        type=str,
        required=True,
        help="path to nuage_patching_config.yaml")
    args = parser.parse_args()

    with open(args.nuage_config) as nuage_config:
        try:
            nuage_config = yaml.load(nuage_config)
        except yaml.YAMLError as exc:
            logger.error(
                'Error parsing file {filename}: {exc}. Please fix and try '
                'again with correct yaml file.'.format(filename=args.nuage_config, exc=exc))
            sys.exit(1)
    logger.info("nuage_overcloud_full_patch.py was run with following config options %s " % nuage_config)
    check_config(nuage_config)
    image_patching(nuage_config)


if __name__ == "__main__":
    main()
