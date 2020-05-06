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

import subprocess
import sys
import logging
import os
from . import constants


logger = logging.getLogger(constants.LOG_FILE_NAME)


#####
# Function to run commands on the console
#####


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
        output_list.append(out.decode())

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
        [constants.VIRT_CUSTOMIZE_ENV + 'virt-customize '
                                        '--run-command %s' %
         command])


def virt_customize_run(command):
    return cmds_run([constants.VIRT_CUSTOMIZE_ENV + 'virt-customize '
                                                    '--run %s' %
                     command])


def virt_copy(command):
    return cmds_run([constants.VIRT_CUSTOMIZE_ENV + 'virt-copy-in '
                                                    '-a %s' % command])


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
    cmds = '''#!/bin/bash
set -xe
'''
    constants.PATCHING_SCRIPT += cmds


#####
# Function that writes commands to a file
#####

def write_to_file(contents):
    if os.path.isfile(constants.SCRIPT_NAME):
        os.remove(constants.SCRIPT_NAME)

    with open(constants.SCRIPT_NAME, 'a') as script:
        script.writelines(contents)

#####
# Importing Gpgkeys to Overcloud image
#####


def importing_gpgkeys(image, gpgkeys):
    cmd = '''
#### Importing GPG keys
'''
    constants.PATCHING_SCRIPT += cmd
    for gpgkey in gpgkeys:
        file_exist = os.path.isfile(gpgkey)
        file_name = os.path.basename(gpgkey)
        if file_exist:
            virt_copy('%s %s %s' % (image, gpgkey,
                                    constants.TEMPORARY_PATH))
            rpm_import = '''
rpm --import %s%s
''' % (constants.TEMPORARY_PATH, file_name)
            constants.PATCHING_SCRIPT += rpm_import

        else:
            logger.error("Nuage package signing key is not present "
                         "in %s ,"
                         "Installation cannot proceed.  Please place "
                         "the "
                         "signing key in the correct location and"
                         " retry" %
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


#####
# Function to add RHEL subscription using guestfish
#####


def rhel_subscription(username, password, pool, satellite_url, satellite_org,
                      satellite_key, proxy_hostname, proxy_port,
                      rhel_sub_type):
    subscription_command = ''
    if proxy_hostname and proxy_port:
        subscription_command += (
                "subscription-manager config"
                " --server.proxy_hostname=%s "
                " --server.proxy_port=%s\n"
                % (proxy_hostname, proxy_port)
        )
    # this does not allow multiple runs of the patching script
    if rhel_sub_type == constants.RHEL_SUB_SATELLITE:
        subscription_command += (
            "hostname nuage-patching\n"
            "sudo curl -k %(0)s/pub/katello-ca-consumer-latest.noarch.rpm -o "
            "%(1)skatello-ca-consumer-latest.noarch.rpm\n"
            "sudo rpm -Uvh %(1)skatello-ca-consumer-latest.noarch.rpm\n"
            "rm -rf %(1)skatello-ca-consumer-latest.noarch.rpm\n"
            % {'0': satellite_url, '1': constants.TEMPORARY_PATH}
        )
        subscription_command += (
            "subscription-manager register"
            " --org='%s' --activationkey='%s'\n" %
            (satellite_org, satellite_key)
        )
    else:
        subscription_command += (
            "subscription-manager register"
            " --username='%s' --password='%s' --force \n" % (username, password)
        )
        subscription_command += (
            "subscription-manager attach --pool='%s'\n" % pool
        )
    subscription_command += (
        "sudo subscription-manager repos "
        "--enable=rhel-8-for-x86_64-baseos-rpms "
        "--enable=rhel-8-for-x86_64-appstream-rpms  "
        "--enable=rhel-8-for-x86_64-highavailability-rpms \n "
    )
    constants.PATCHING_SCRIPT += subscription_command


#####
# Function to remove the RHEL subscription
#####


def rhel_remove_subscription(rhel_sub_type=None):
    cmd = '''
#### Removing RHEL Subscription
subscription-manager unregister
'''
    if rhel_sub_type == constants.RHEL_SUB_SATELLITE:
        cmd += (
            "rpm -qa"
            "| grep katello-ca-consumer"
            "| xargs sudo rpm -e"
        )
    constants.PATCHING_SCRIPT += cmd

#####
# Function to install packages nuage python ovs
#####


def install_nuage_python_ovs_packages():
    cmd = '''
#### Install Nuage Python OpenvSwitch
yum install --setopt=skip_missing_names_on_install=False -y %s
yum clean all
''' % constants.NUAGE_PYTHON_OVS
    constants.PATCHING_SCRIPT += cmd

#####
# Function to remove packages that are not needed
#####


def uninstall_packages():
    cmd = '''
#### Removing Upstream OpenvSwitch
ovs_package_name=$(rpm -qa | awk -F- \
'/^(openvswitch[0-9]+\.[0-9]+-|openvswitch-2)/{print $1}')
yum remove -y $ovs_package_name network-scripts-$ovs_package_name --noautoremove
yum clean all
'''
    constants.PATCHING_SCRIPT += cmd
