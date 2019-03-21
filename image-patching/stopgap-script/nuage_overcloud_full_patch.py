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
# Version     : Version of OSP Director 13
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
NUAGE_PACKAGES="nuage-metadata-agent nuage-puppet-modules selinux-policy-nuage nuage-bgp nuage-openstack-neutronclient"
NUAGE_DEPENDENCIES="libvirt perl-JSON python-novaclient openstack-neutron-sriov-nic-agent lldpad"
NUAGE_VRS_PACKAGE = "nuage-openvswitch"
VIRT_CUSTOMIZE_MEMSIZE = "2048"

### Gpg values
GPGCHECK=0
GPGKEY=''

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
    cmds_run(['echo " --RpmPublicKey=GPG Key"'])
    cmds_run(['echo " --no-signing-key=Image patching proceeds with package signature verification disabled "'])
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
# Function to add files based on the version
#####

def add_files(image, version, workingDir):
    version = int(version)
    if version == 13:
        cmds_run(['cat <<EOT > version_13 \n'
        'cp /etc/puppet/modules/nuage/manifests/13_files/neutron_init.pp /etc/puppet/modules/neutron/manifests/init.pp \n'
        'cp /etc/puppet/modules/nuage/manifests/13_files/conductor.pp /etc/puppet/modules/ironic/manifests/conductor.pp \n'
        'EOT'])
        virt_customize(
            '"mkdir -p /etc/puppet/modules/nuage/manifests/13_files" -a %s --memsize %s --selinux-relabel' % (
            image, VIRT_CUSTOMIZE_MEMSIZE))
        virt_copy('%s %s/13_files/* /etc/puppet/modules/nuage/manifests/13_files' % (image, workingDir))
        virt_customize_run('version_13 -a %s --memsize %s --selinux-relabel' %( image, VIRT_CUSTOMIZE_MEMSIZE))
        
        cmds_run(['rm -f version_13'])


        
#####
# Function to copy GPG Key to Overcloud image
#####

def copy_gpg(image, workingDir, gpg_file):
    virt_copy('%s %s/%s /tmp' % (image, workingDir, gpg_file))
    
#####
# Function to delete GPG Key from Overcloud image
#####   
def delete_gpg(image, gpg_file):
    virt_customize('"rm -f /tmp/%s" -a %s --selinux-relabel' % (gpg_file, image))
    
        
        
#####
# Function to install Nuage packages that are required
#####

def install_packages(image):
    cmds_run(['cat <<EOT > nuage_packages \n'
              'yum install %s -y \n'
              'yum install %s -y \n'
              'yum install %s -y \n'
              'EOT' % (NUAGE_DEPENDENCIES, NUAGE_PACKAGES, NUAGE_VRS_PACKAGE)])
    virt_customize_run('nuage_packages -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f nuage_packages'])

#####
# Function to create the repo file
#####

def create_repo_file(reponame, repoUrl, image, gpgcheck, gpgkey):
    create_repo = 'cat <<EOT > create_repo \n' \
                  'touch /etc/yum.repos.d/nuage.repo \n' \
                  'echo "[Nuage]" >> /etc/yum.repos.d/nuage.repo \n' \
                  'echo "name=%s" >> /etc/yum.repos.d/nuage.repo \n' \
                  'echo "baseurl=%s" >> /etc/yum.repos.d/nuage.repo \n' \
                  'echo "enabled = 1" >> /etc/yum.repos.d/nuage.repo \n' \
                  'echo "gpgcheck = %s" >> /etc/yum.repos.d/nuage.repo \n' \
                  'echo "gpgkey = file://%s" >> /etc/yum.repos.d/nuage.repo \n' \
                  'EOT' % (reponame, repoUrl, gpgcheck, gpgkey)

    cmds_run([create_repo])
    virt_customize_run('create_repo -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f create_repo'])


#####
# Function to clean up the repo file
#####
def delete_repo_file(image):
    virt_customize('"rm -f /etc/yum.repos.d/nuage.repo" -a %s --selinux-relabel' % (image))
    


#####
# Function to install Nuage AVRS packages that are required
#####

def copy_avrs_packages(image, avrs_baseurl, proxy_hostname = None, proxy_port = None):
    if proxy_hostname != None and proxy_port != None:
        avrs_cmds = 'cat <<EOT > nuage_avrs_packages \n' \
                    'export http_proxy=http://%s:%s \n' \
                    'export https_proxy=http://%s:%s \n'% (proxy_hostname, proxy_port, proxy_hostname, proxy_port)
    else:
        avrs_cmds = 'cat <<EOT > nuage_avrs_packages \n'

    avrs_cmds = avrs_cmds + 'mkdir ./6wind \n' \
                            'rm -rf /var/cache/yum/Nuage \n' \
                            'yum clean all \n' \
                            'touch /kernel-version \n' \
                            'rpm -q kernel | awk \'{ print substr(\$1,8) }\' > /kernel-version \n' \
                            'yum install -y createrepo \n' \
                            'yum install --downloadonly --downloaddir=./6wind kernel-headers-\$(cat /kernel-version) kernel-devel-\$(cat /kernel-version) kernel-debug-devel-\$(cat /kernel-version) python-pyelftools* dkms* 6windgate* nuage-openvswitch nuage-metadata-agent virtual-accelerator* \n' \
                            'yum install --downloadonly --downloaddir=./6wind selinux-policy-nuage-avrs* \n' \
                            'yum install --downloadonly --downloaddir=./6wind 6wind-openstack-extensions \n' \
                            'rm -rf /kernel-version \n' \
                            'EOT'

    cmds_run([avrs_cmds])
    virt_customize_run('nuage_avrs_packages -a %s --memsize %s --selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f nuage_avrs_packages'])



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
		    if '--no-signing-key' in args:
                        argsDict['no-signing-key'] = ''
                        continue
                    else:
			logger.error("Some of the keys provided in input arguments doesnt have proper values")
                        raise show_help()
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

        if 'RpmPublicKey' not in argsDict and 'no-signing-key' not in argsDict:

            logger.error("'--RpmPublicKey' or '--no-signing-key' are not passed in image patching command, If verification of Nuage-supplied packages is not required, please restart image patching with the --no-signing-key option.")
            sys.exit(1)
            
        if 'no-signing-key' in argsDict:

            logger.warning("Image patching proceeding with package signature verification disabled. Nuage packages installed will not have package signatures verified.")
	        global GPGCHECK, GPGKEY
        cmds_run(['echo "Verifying pre-requisite packages for script"'])
        
        libguestfs = cmds_run(['rpm -q libguestfs-tools-c'])
        if 'not installed' in libguestfs:
            cmds_run(['echo "Please install libguestfs-tools-c package for the script to run"'])
            sys.exit()

        if 'RpmPublicKey' in argsDict:
            file_exists = os.path.isfile(argsDict['RpmPublicKey'][0])
            if file_exists:
               GPGCHECK = 1
               GPGKEY = '/tmp/' + argsDict['RpmPublicKey'][0]
               cmds_run(['echo "Copying GpgKey"'])
               copy_gpg(argsDict['ImageName'][0], workingDir, argsDict['RpmPublicKey'][0])
            else:
               logger.error("Nuage package signing key is not present in %s ,Installation cannot proceed.  Please place the signing key in the correct location and retry" %(argsDict['RpmPublicKey'][0]))
               sys.exit(1)


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
            
            create_repo_file(argsDict['RepoName'][0], argsDict['RepoBaseUrl'][0], argsDict['ImageName'][0], GPGCHECK, GPGKEY)
                
        else:
            
            create_repo_file('Nuage', argsDict['RepoBaseUrl'][0], argsDict['ImageName'][0], GPGCHECK, GPGKEY)

        cmds_run(['echo "Installing Nuage Packages"'])
        install_packages(argsDict['ImageName'][0])

        cmds_run(['echo "Cleaning up"'])

        delete_repo_file(argsDict['ImageName'][0])
        

        if 'AVRSBaseUrl' in argsDict:
            
            create_repo_file('6wind', argsDict['RepoBaseUrl'][0], argsDict['ImageName'][0], GPGCHECK, GPGKEY)

            cmds_run(['echo "Downloading AVRS Packages"'])
            if 'ProxyHostname' in argsDict and 'ProxyPort' in argsDict:
                copy_avrs_packages(argsDict['ImageName'][0], argsDict['AVRSBaseUrl'][0], argsDict['ProxyHostname'][0], argsDict['ProxyPort'][0])
            else:
                copy_avrs_packages(argsDict['ImageName'][0], argsDict['AVRSBaseUrl'][0])

            cmds_run(['echo "Cleaning up"'])
            delete_repo_file(argsDict['ImageName'][0])

        if GPGCHECK:
            delete_gpg(argsDict['ImageName'][0], argsDict['RpmPublicKey'][0])
            
        if 'RhelUserName' in argsDict and 'RhelPassword' in argsDict and 'RhelPool' in argsDict:
            rhel_remove_subscription(argsDict['ImageName'][0])

        cmds_run(['echo "Adding files post-patching"'])
        add_files(argsDict['ImageName'][0], argsDict['Version'][0], workingDir)

        cmds_run(['echo "Done"'])


if __name__ == "__main__":
    main(sys.argv)
