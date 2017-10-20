import subprocess
import sys
import logging
import os
from logging import handlers

#
# This script is used to patch an existing OpenStack
# image with Nuage components
#
# This script takes in following input parameters:
# RhelUserName: User name for the RHEL subscription
# RhelPassword: Password for the RHEL subscription
# RhelPool    : RHEL Pool to subscribe
# RepoName    : Name of the local repository
# RepoBaseUrl : Base URL of the local repository
# Version     : Version of OSP Director (7 or 8)
#
# The following sequence is executed by the script
# 1. Subscribe to RHEL and the pool
# 2. Uninstall OVS
# 3. Create the local repo file for Nuage packages
# 4. Install neutron-client, netlib, metadata agent
# 5. Install VRS
# 6. Unsubscribe from RHEL
# 7. Add the files post-patching
#
#

### List of Nuage packages
NUAGE_PACKAGES="nuage-openstack-neutron nuage-openstack-neutronclient nuage-metadata-agent nuage-puppet-modules nuage-openstack-heat nuage-openstack-horizon selinux-policy-nuage nuage-nova-extensions"
NUAGE_DEPENDENCIES="libvirt perl-JSON python-novaclient openstack-neutron-sriov-nic-agent lldpad"
NUAGE_VRS_PACKAGE = "nuage-openvswitch"
VIRT_CUSTOMIZE_MEMSIZE = "2048"

logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                shell=True, close_fds=True)
        (out, err) = proc.communicate()
        if err and err.split():
            logger.error("error occurred during command:\n"
                         " %s\n error:\n %s \n exiting" %
                         (cmd, err))
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
    return cmds_run(['export LIBGUESTFS_BACKEND=direct;virt-customize --run-command %s' % command])


def virt_customize_run(command):
    return cmds_run(['export LIBGUESTFS_BACKEND=direct;virt-customize --run %s' % command])


def virt_copy(command):
    return cmds_run(['export LIBGUESTFS_BACKEND=direct;virt-copy-in -a %s' % command])


#####
# Function to print help message
#####

def show_help():
    cmds_run(['echo "Options are"'])
    cmds_run(['echo " --ImageName= Name of the qcow2 image (overcloud-full.qcow2 for example)"'])
    cmds_run(['echo " --RhelUserName=User name for RHELSubscription"'])
    cmds_run(['echo " --RhelPassword=Password for the RHEL Subscription"'])
    cmds_run(['echo " --RhelPool=Pool to subscribe to for base packages"'])
    cmds_run(['echo " --RepoName=Name for the local repo hosting the Nuage RPMs"'])
    cmds_run(['echo " --RepoBaseUrl=Base URL for the repo hosting the Nuage RPMs"'])
    cmds_run(['echo " --Version=OSP-Director version (10)"'])
    cmds_run(['echo " -h or --help: Show this message"'])


#####
# Function to add RHEL subscription using guestfish
#####

def rhel_subscription(username, password, pool, image, proxy_hostname = None, proxy_port = None):
    subscription_command = ''
    if proxy_hostname != None:
        subscription_command = subscription_command + 'cat <<EOT > rhel_subscription \n' \
                                                      'subscription-manager config --server.proxy_hostname=%s' \
                                                      ' --server.proxy_port=%s \n' % (proxy_hostname, proxy_port)
    else:
        subscription_command = subscription_command + 'cat <<EOT > rhel_subscription \n'

    subscription_command = subscription_command + 'subscription-manager register --username=%s --password=\'%s\' \n' \
                                                  'subscription-manager subscribe --pool=%s \n' \
                                                  'subscription-manager repos --enable=rhel-7-server-optional-rpms \n' \
                                                  'subscription-manager repos --enable=rhel-7-server-rpms \n' \
                                                  'EOT' % (username, password, pool)
    cmds_run([subscription_command])
    virt_customize_run('rhel_subscription -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))

    cmds_run(['rm -f rhel_subscription'])


#####
# Function to add files based on the version
#####

def add_files(image, version, workingDir):
    version = int(version)
    if version == 7:
        virt_customize('"mkdir -p /etc/puppet/modules/nuage/manifests/7_files" -a %s --memsize %s --selinux-relabel' % (
        image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_copy(
            '%s %s/7_files/neutron_plugin_nuage.rb /etc/puppet/modules/nuage/manifests/7_files' % (image, workingDir))
        virt_copy('%s %s/7_files/impl_ifcfg.py /etc/puppet/modules/nuage/manifests/7_files' % (image, workingDir))
        virt_copy('%s %s/7_files/ini_setting.rb /etc/puppet/modules/nuage/manifests/7_files' % (image, workingDir))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/7_files/neutron_plugin_nuage.rb /etc/puppet/modules/neutron/lib/puppet/type/neutron_plugin_nuage.rb" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/7_files/ini_setting.rb /etc/puppet/modules/neutron/lib/puppet/provider/neutron_plugin_nuage/ini_setting.rb" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/7_files/impl_ifcfg.py /usr/lib/python2.7/site-packages/os_net_config/impl_ifcfg.py" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))

    if version == 8:
        virt_customize(
            '"mkdir -p /etc/puppet/modules/nuage/manifests/8_files" - a %s - -memsize %s - -selinux - relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_copy(
            '%s %s/8_files/neutron_plugin_nuage.rb /etc/puppet/modules/nuage/manifests/8_files' % (image, workingDir))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/8_files/neutron_plugin_nuage.rb /etc/puppet/modules/neutron/lib/puppet/type/neutron_plugin_nuage.rb" - a %s - -memsize %s - -selinux - relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))

    if version == 9:
        virt_customize('"mkdir -p /etc/puppet/modules/nuage/manifests/9_files" -a %s --memsize %s --selinux-relabel' % (
        image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_copy('%s %s/9_files/nuage.pp /etc/puppet/modules/nuage/manifests/9_files' % (image, workingDir))
        virt_copy(
            '%s %s/9_files/neutron-server.service /etc/puppet/modules/nuage/manifests/9_files' % (image, workingDir))
        virt_copy('%s %s/9_files/ml2.pp /etc/puppet/modules/nuage/manifests/9_files' % (image, workingDir))
        virt_copy('%s %s/9_files/filter.pp /etc/puppet/modules/nuage/manifests/9_files' % (image, workingDir))
        virt_copy('%s %s/9_files/grub /etc/puppet/modules/nuage/manifests/9_files' % (image, workingDir))
        virt_copy('%s %s/9_files/sriov.pp /etc/puppet/modules/nuage/manifests/9_files' % (image, workingDir))
        virt_copy('%s %s/9_files/topology-collector-4.7.0.tar.gz /etc/puppet/modules/nuage/manifests/9_files' % (
        image, workingDir))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/9_files/nuage.pp /etc/puppet/modules/neutron/manifests/plugins/nuage.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/9_files/neutron-server.service /usr/lib/systemd/system/neutron-server.service" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/9_files/ml2.pp /etc/puppet/modules/neutron/manifests/plugins/ml2.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/9_files/filter.pp /etc/puppet/modules/nova/manifests/scheduler/filter.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/9_files/grub /etc/default/grub" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/9_files/sriov.pp /etc/puppet/modules/neutron/manifests/agents/ml2/sriov.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/9_files/topology-collector-4.7.0.tar.gz /root/topology-collector-4.7.0.tar.gz" -a %s --memsize %s --selinux-relabe' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))

    if version == 10:
        virt_customize('"mkdir -p /etc/puppet/modules/nuage/manifests/10_files" -a %s --memsize %s --selinux-relabel' %( image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_copy('%s %s/10_files/config.pp /etc/puppet/modules/nuage/manifests/10_files' % (image, workingDir))
        virt_copy('%s %s/10_files/nuage.pp /etc/puppet/modules/nuage/manifests/10_files'  % (image, workingDir))
        virt_copy('%s %s/10_files/ml2.pp /etc/puppet/modules/nuage/manifests/10_files' % (image, workingDir))
        virt_copy('%s %s/10_files/tripleo_profile_nuage.pp /etc/puppet/modules/nuage/manifests/10_files'  % (image, workingDir))
        virt_copy('%s %s/10_files/tripleo_profile_sriov.pp /etc/puppet/modules/nuage/manifests/10_files' % (image, workingDir))
        virt_copy('%s %s/10_files/init.pp /etc/puppet/modules/nuage/manifests/10_files' % (image, workingDir))
        virt_copy('%s %s/10_files/local_settings.py.erb /etc/puppet/modules/nuage/manifests/10_files' % (image, workingDir))
        virt_customize('"mkdir -p /etc/puppet/modules/nova/manifests/patch" -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize('"cp /etc/puppet/modules/nuage/manifests/10_files/config.pp /etc/puppet/modules/nova/manifests/patch/config.pp" -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize('"cp /etc/puppet/modules/nuage/manifests/10_files/nuage.pp /etc/puppet/modules/neutron/manifests/plugins/ml2/nuage.pp" -a %s --memsize %s --selinux-relabel' %(image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize('"cp /etc/puppet/modules/nuage/manifests/10_files/ml2.pp /etc/puppet/modules/tripleo/manifests/profile/base/neutron/plugins/ml2.pp" -a %s --memsize %s --selinux-relabel' %(image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize('"cp /etc/puppet/modules/nuage/manifests/10_files/tripleo_profile_nuage.pp /etc/puppet/modules/tripleo/manifests/profile/base/neutron/plugins/ml2/nuage.pp" -a %s --memsize %s --selinux-relabel' %(image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize('"cp /etc/puppet/modules/nuage/manifests/10_files/tripleo_profile_sriov.pp /etc/puppet/modules/tripleo/manifests/profile/base/neutron/sriov.pp" -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/10_files/init.pp /etc/puppet/modules/horizon/manifests/init.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/10_files/local_settings.py.erb /etc/puppet/modules/horizon/templates/local_settings.py.erb" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))

    if version == 11:
        virt_customize(
            '"mkdir -p /etc/puppet/modules/nuage/manifests/11_files" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_copy('%s %s/11_files/config.pp /etc/puppet/modules/nuage/manifests/11_files' % (image, workingDir))
        virt_copy('%s %s/11_files/nuage.pp /etc/puppet/modules/nuage/manifests/11_files' % (image, workingDir))
        virt_copy('%s %s/11_files/ml2.pp /etc/puppet/modules/nuage/manifests/11_files' % (image, workingDir))
        virt_copy('%s %s/11_files/tripleo_profile_nuage.pp /etc/puppet/modules/nuage/manifests/11_files' % (
        image, workingDir))
        virt_copy('%s %s/11_files/tripleo_profile_sriov.pp /etc/puppet/modules/nuage/manifests/11_files' % (
        image, workingDir))
        virt_copy('%s %s/11_files/init.pp /etc/puppet/modules/nuage/manifests/11_files' % (image, workingDir))
        virt_copy(
            '%s %s/11_files/local_settings.py.erb /etc/puppet/modules/nuage/manifests/11_files' % (image, workingDir))
        virt_customize('"mkdir -p /etc/puppet/modules/nova/manifests/patch" -a %s --memsize %s --selinux-relabel' % (
        image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/11_files/config.pp /etc/puppet/modules/nova/manifests/patch/config.pp" -a %s --memsize %s --selinux-relabel' % (
                image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/11_files/nuage.pp /etc/puppet/modules/neutron/manifests/plugins/ml2/nuage.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/11_files/ml2.pp /etc/puppet/modules/tripleo/manifests/profile/base/neutron/plugins/ml2.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/11_files/tripleo_profile_nuage.pp /etc/puppet/modules/tripleo/manifests/profile/base/neutron/plugins/ml2/nuage.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/11_files/tripleo_profile_sriov.pp /etc/puppet/modules/tripleo/manifests/profile/base/neutron/sriov.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/11_files/init.pp /etc/puppet/modules/horizon/manifests/init.pp" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_customize(
            '"cp /etc/puppet/modules/nuage/manifests/11_files/local_settings.py.erb /etc/puppet/modules/horizon/templates/local_settings.py.erb" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))


#####
# Function to remove the RHEL subscription
#####

def rhel_remove_subscription(image):
    cmds_run(['cat <<EOT > rhel_unsubscribe \n'
              'subscription-manager unregister \n'
              'EOT'])
    virt_customize_run('rhel_unsubscribe -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f rhel_unsubscribe'])


#####
# Function to remove packages that are not needed
#####

def uninstall_packages(image, version):
    # For Newton and above, use standard python-openvswitch
    if version <= 9:
        virt_customize(
            '"yum remove python-openvswitch -y" -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
    virt_customize('"yum remove openvswitch -y" -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))


#####
# Function to install Nuage packages that are required
#####

def install_packages(image):
    cmds_run(['cat <<EOT > nuage_packages \n'
              'yum install %s -y \n'
              'yum install %s -y \n'
              'EOT' % (NUAGE_DEPENDENCIES, NUAGE_PACKAGES)])
    virt_customize_run('nuage_packages -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f nuage_packages'])


#####
# Installing VRS and the dependencies for VRS
#####

def install_vrs(image):
    cmds_run(['cat <<EOT > vrs_packages \n'
              'yum install %s -y \n'
              'EOT' % (NUAGE_VRS_PACKAGE)])
    virt_customize_run('vrs_packages -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f vrs_packages'])


#####
# Function to create the repo file
#####

def create_repo_file(reponame, repoUrl, image):
    cmds_run(['cat <<EOT > create_repo \n'
              'touch /etc/yum.repos.d/nuage.repo \n'
              'echo "[Nuage]" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "name=%s" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "baseurl=%s" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "enabled = 1" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "gpgcheck = 0" >> /etc/yum.repos.d/nuage.repo \n'
              'EOT' % (reponame, repoUrl)])
    virt_customize_run('create_repo -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))


#####
# Function to clean up the repo file
#####
def delete_repo_file(reponame, repoUrl, image):
    cmds_run(['cat <<EOT > create_repo \n'
              'touch /etc/yum.repos.d/nuage.repo \n'
              'echo "[Nuage]" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "name=%s" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "baseurl=%s" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "enabled = 1" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "gpgcheck = 0" >> /etc/yum.repos.d/nuage.repo \n'
              'EOT' % (reponame, repoUrl)])
    virt_customize('"rm -f /etc/yum.repos.d/nuage.repo" -a %s --selinux-relabel' % (image))
    cmds_run(['rm -f create_repo'])


def main(args):
    argsDict = {}
    if len(args) < 3:
        show_help()
    else:
        for inputArg in args:
            if inputArg.startswith('--'):
                try:
                    (key, val) = inputArg.split("=")
                except ValueError:
                    continue
                key = key[2:]
                argsDict[key] = [val]

        if '-h' in argsDict or '--help' in argsDict:
            show_help()
            sys.exit()

        if 'logFile' in argsDict:
            handler = logging.FileHandler(argsDict['logFile'][0])
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        workingDir = os.path.dirname(os.path.abspath(__file__))

        cmds_run(['echo "Verifying pre-requisite packages for script"'])
        libguestfs = cmds_run(['rpm -q libguestfs-tools-c'])
        if 'not installed' in libguestfs:
            cmds_run(['echo "Please install libguestfs-tools-c package for the script to run"'])
            sys.exit()

        if 'RhelUserName' in argsDict and 'RhelPassword' in argsDict and 'RhelPool' in argsDict:
            cmds_run(['echo "Creating the RHEL subscription"'])
            if 'ProxyHostname' in argsDict and 'ProxyPort' in argsDict:
                rhel_subscription(argsDict['RhelUserName'][0], argsDict['RhelPassword'][0], argsDict['RhelPool'][0],
                              argsDict['ImageName'][0], argsDict['ProxyHostname'][0], argsDict['ProxyPort'][0])
            else:
                rhel_subscription(argsDict['RhelUserName'][0], argsDict['RhelPassword'][0], argsDict['RhelPool'][0],
                                  argsDict['ImageName'][0])

        cmds_run(['echo "Uninstalling packages"'])
        uninstall_packages(argsDict['ImageName'][0], argsDict['Version'][0])

        cmds_run(['echo "Creating Repo File"'])
        if 'RepoName' in argsDict:
            create_repo_file(argsDict['RepoName'][0], argsDict['RepoBaseUrl'][0], argsDict['ImageName'][0])
        else:
            create_repo_file('Nuage', argsDict['RepoBaseUrl'][0], argsDict['ImageName'][0])

        cmds_run(['echo "Installing Nuage Packages"'])
        install_packages(argsDict['ImageName'][0])

        cmds_run(['echo "Installing VRS"'])
        install_vrs(argsDict['ImageName'][0])

        cmds_run(['echo "Cleaning up"'])
        if 'RepoName' in argsDict:
            delete_repo_file(argsDict['RepoName'][0], argsDict['RepoBaseUrl'][0], argsDict['ImageName'][0])
        else:
            delete_repo_file('Nuage', argsDict['RepoBaseUrl'][0], argsDict['ImageName'][0])

        if 'RhelUserName' in argsDict and 'RhelPassword' in argsDict and 'RhelPool' in argsDict:
            rhel_remove_subscription(argsDict['ImageName'][0])

        cmds_run(['echo "Adding files post-patching"'])
        add_files(argsDict['ImageName'][0], argsDict['Version'][0], workingDir)

        cmds_run(['echo "Done"'])


if __name__ == "__main__":
    main(sys.argv)