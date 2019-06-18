import argparse
import subprocess
import sys
import logging
import os

#
# This script is used to patch an existing OpenStack
# image with Nuage components
#
# This script takes in following input parameters:
# RhelUserName: User name for the RHEL subscription
# RhelPassword: Password for the RHEL subscription
# RhelPool    : RHEL Pool to subscribe
# RepoName    : Name of the local repository
# RepoBaseUrl : URL to the repository for Nuage VRS and OpenStack
# packages to be installed
# RpmPublicKey   : RPM GPG Key (repeat option to set multiple RPM GPG
#  Keys)
# no-signing-key : Image patching proceeds with package signature
# verification disabled
# logFile        : Log file name
#
# The following sequence is executed by the script
# 1. Subscribe to RHEL and the pool
# 2. Uninstall OVS
# 3. Create the local repo file for Nuage packages
# 4. Install neutron-client, metadata agent and VRS
# 5. Unsubscribe from RHEL
# 6. Add the files post-patching
#
#

### List of Nuage packages
NUAGE_PACKAGES = "nuage-metadata-agent nuage-puppet-modules " \
                 "selinux-policy-nuage nuage-bgp " \
                 "nuage-openstack-neutronclient"
NUAGE_DEPENDENCIES = "libvirt perl-JSON python-novaclient " \
                     "openstack-neutron-sriov-nic-agent lldpad"
NUAGE_VRS_PACKAGE = "nuage-openvswitch"
VIRT_CUSTOMIZE_MEMSIZE = "2048"
GPGCHECK = 1

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
    return cmds_run(['export '
                     'LIBGUESTFS_BACKEND=direct;virt-customize '
                     '--run-command %s' % command])


def virt_customize_run(command):
    return cmds_run(['export '
                     'LIBGUESTFS_BACKEND=direct;virt-customize '
                     '--run %s' % command])


def virt_copy(command):
    return cmds_run(['export '
                     'LIBGUESTFS_BACKEND=direct;virt-copy-in -a '
                     '%s' % command])


#####
# Function to add RHEL subscription using guestfish
#####

def rhel_subscription(username, password, pool, image,
                      proxy_hostname=None, proxy_port=None):
    subscription_command = ''
    if proxy_hostname != None:
        subscription_command = subscription_command + \
                               'cat <<EOT > ' \
                               'rhel_subscription \n' \
                               'subscription-manager config ' \
                               '--server.proxy_hostname=%s' \
                               ' --server.proxy_port=%s \n' % (
                               proxy_hostname, proxy_port)
    else:
        subscription_command = subscription_command + \
                               'cat <<EOT > ' \
                               'rhel_subscription \n'

    subscription_command = subscription_command + \
                           'subscription-manager register ' \
                           '--username=%s --password=\'%s\' \n' \
                           'subscription-manager subscribe ' \
                           '--pool=%s \n' \
                           'subscription-manager repos ' \
                           '--enable=rhel-7-server-optional-rpms \n' \
                           'subscription-manager repos ' \
                           '--enable=rhel-7-server-rpms \n' \
                           'EOT' % (
                           username, password, pool)
    cmds_run([subscription_command])
    virt_customize_run(
        'rhel_subscription -a %s --memsize %s --selinux-relabel '
        '--edit \'/usr/lib/systemd/system/rhel-autorelabel.service: '
        '$_ = "" if /StandardInput=tty/\'' % (
        image, VIRT_CUSTOMIZE_MEMSIZE))

    cmds_run(['rm -f rhel_subscription'])


#####
# Function to remove the RHEL subscription
#####

def rhel_remove_subscription(image):
    cmds_run(['cat <<EOT > rhel_unsubscribe \n'
              'subscription-manager unregister \n'
              'EOT'])
    virt_customize_run(
        'rhel_unsubscribe -a %s --memsize %s --selinux-relabel --edit '
        '\'/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" '
        'if /StandardInput=tty/\'' % (
        image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f rhel_unsubscribe'])


#####
# Function to remove packages that are not needed
#####

def uninstall_packages(image):
    virt_customize(
        '"yum remove openvswitch[0-9]* -y" -a %s --memsize %s '
        '--selinux-relabel --edit '
        '\'/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" '
        'if /StandardInput=tty/\'' % (
        image, VIRT_CUSTOMIZE_MEMSIZE))


#####
# Function to install Nuage packages that are required
#####

def install_packages(image):
    cmds_run(['cat <<EOT > nuage_packages \n'
              'yum install %s -y \n'
              'yum install %s -y \n'
              'yum install %s -y \n'
              'EOT' % (
              NUAGE_DEPENDENCIES, NUAGE_PACKAGES, NUAGE_VRS_PACKAGE)])
    virt_customize_run(
        'nuage_packages -a %s --memsize %s --selinux-relabel --edit '
        '\'/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" '
        'if /StandardInput=tty/\'' % (
        image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f nuage_packages'])


#####
# Function to create the repo file
#####

def create_repo_file(reponame, repoUrl, image, gpgcheck):
    cmds_run(['cat <<EOT > create_repo \n'
              'touch /etc/yum.repos.d/nuage.repo \n'
              'echo "[Nuage]" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "name=%s" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "baseurl=%s" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "enabled = 1" >> /etc/yum.repos.d/nuage.repo \n'
              'echo "gpgcheck = %s" >> /etc/yum.repos.d/nuage.repo \n'
              'EOT' % (reponame, repoUrl, gpgcheck)])
    virt_customize_run(
        'create_repo -a %s --memsize %s --selinux-relabel --edit '
        '\'/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" '
        'if /StandardInput=tty/\'' % (
        image, VIRT_CUSTOMIZE_MEMSIZE))


#####
# Function to clean up the repo file
#####
def delete_repo_file(image):
    virt_customize(
        '"rm -f /etc/yum.repos.d/nuage.repo" -a %s --selinux-relabel '
        '--edit \'/usr/lib/systemd/system/rhel-autorelabel.service: '
        '$_ = "" if /StandardInput=tty/\'' % (image))


#####
# Importing Gpgkeys to Overcloud image
#####

def importing_gpgkeys(image, workingDir, gpgkeys):
    for gpgkey in gpgkeys:
        file_exists = os.path.isfile(gpgkey[0])
        if file_exists:
            virt_copy('%s %s/%s /tmp/' % (image, workingDir, gpgkey[0]))
            virt_customize(
                '"rpm --import /tmp/%s" -a %s --memsize %s '
                '--selinux-relabel' % (
                    gpgkey[0], image, VIRT_CUSTOMIZE_MEMSIZE))
        else:
            logger.error(
                "Nuage package signing key is not present in %s ,"
                "Installation cannot proceed.  Please place the "
                "signing key in the correct location and retry" % (
                    gpgkey[0]))
            sys.exit(1)


def image_patching(args):

    global GPGCHECK

    if args.logFile:
        handler = logging.FileHandler(args.logFile)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    workingDir = os.path.dirname(os.path.abspath(__file__))

    if not args.no_signing_key and args.RpmPublicKey == None:
        logger.error(
            "'--RpmPublicKey' or '--no_signing_key' are not passed in "
            "image patching command, If verification of "
            "Nuage-supplied packages is not required, please restart "
            "image patching with the --no_signing_key option.")
        sys.exit(1)

    if args.no_signing_key:
        logger.warning(
            "Image patching proceeding with package signature "
            "verification disabled. Nuage packages installed will not "
            "have package signatures verified.")
        GPGCHECK = 0

    cmds_run(['echo "Verifying pre-requisite packages for script"'])
    libguestfs = cmds_run(['rpm -q libguestfs-tools-c'])
    if 'not installed' in libguestfs:
        cmds_run(['echo "Please install libguestfs-tools-c package '
                  'for the script to run"'])
        sys.exit()

    if args.RpmPublicKey:
        cmds_run(['echo "Importing gpgkey(s) to overcloud image"'])
        importing_gpgkeys(args.ImageName, workingDir, args.RpmPublicKey)

    if args.RhelUserName and args.RhelPassword and args.RhelPool:
        cmds_run(['echo "Creating the RHEL subscription"'])
        if args.ProxyHostname and args.ProxyPort:
            rhel_subscription(args.RhelUserName, args.RhelPassword,
                              args.RhelPool,
                              args.ImageName, args.ProxyHostname,
                              args.ProxyPort)
        else:
            rhel_subscription(args.RhelUserName, args.RhelPassword,
                              args.RhelPool,
                              args.ImageName)

    cmds_run(['echo "Uninstalling packages"'])
    uninstall_packages(args.ImageName)

    cmds_run(['echo "Creating Repo File"'])
    create_repo_file(args.RepoName, args.RepoBaseUrl, args.ImageName,
                     GPGCHECK)

    cmds_run(['echo "Installing Nuage Packages"'])
    install_packages(args.ImageName)

    cmds_run(['echo "Cleaning up"'])
    delete_repo_file(args.ImageName)

    if args.RhelUserName and args.RhelPassword and args.RhelPool:
        rhel_remove_subscription(args.ImageName)

    cmds_run(['echo "Done"'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ImageName", type=str, required=True,
                        help="Name of the qcow2 image ("
                             "overcloud-full.qcow2 for example)")
    parser.add_argument("--RhelUserName", type=str,
                        help="User name for RHELSubscription")
    parser.add_argument("--RhelPassword", type=str,
                        help="Password for the RHEL Subscription")
    parser.add_argument("--RhelPool", type=str,
                        help="Pool to subscribe to for base packages")
    parser.add_argument("--RepoName", type=str, default='Nuage',
                        help="Name for the local repo hosting the "
                             "Nuage RPMs")
    parser.add_argument("--RepoBaseUrl", type=str, required=True,
                        help="Base URL for the repo hosting the Nuage "
                             "VRS RPMs")
    parser.add_argument("--RpmPublicKey", action='append', nargs=1,
                        help="RPM GPG Key (repeat option to set "
                             "multiple RPM GPG Keys)")
    parser.add_argument("--no-signing-key", dest="no_signing_key",
                        action="store_true",
                        help="Image patching proceeds with package "
                             "signature verification disabled")
    parser.add_argument("--ProxyHostname", type=str,
                        help="Proxy Hostname")
    parser.add_argument("--ProxyPort", type=str, help="Proxy Port")
    parser.add_argument("--logFile", type=str,
                        default='nuage_image_patching.log',
                        help="Log file name")
    args = parser.parse_args()
    image_patching(args)


if __name__ == "__main__":
    main()
