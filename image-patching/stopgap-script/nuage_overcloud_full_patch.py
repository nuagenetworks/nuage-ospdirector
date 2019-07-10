import argparse
import subprocess
import sys
import logging
import os
'''
This script is used to patch an existing OpenStack
image with Nuage components
This script takes in following input parameters:
 RhelUserName : User name for the RHEL subscription
 RhelPassword : Password for the RHEL subscription
 RhelPool     : RHEL Pool to subscribe
 RepoFile     : Name for the file repo hosting the Nuage RPMs
 VRSRepoName  : Name for the local repo hosting the Nuage VRS RPMs
 AVRSRepoName : Name for the local repo hosting the Nuage AVRS RPMs
 RpmPublicKey   : RPM GPG Key (repeat option to set multiple RPM GPG
  Keys)
 no-signing-key : Image patching proceeds with package signature
 verification disabled
 logFile        : Log file name
The following sequence is executed by the script
 1. Subscribe to RHEL and the pool
 2. Uninstall OVS
 3. Download AVRS packages to the image
 4. Install NeutronClient, Nuage-BGP, Selinux Policy Nuage 
    and Nuage Puppet Module
 5. Install VRS, Nuage Metadata Agent
 6. Unsubscribe from RHEL
'''

# List of Nuage packages
NUAGE_PACKAGES = "nuage-puppet-modules selinux-policy-nuage " \
                 "nuage-bgp nuage-openstack-neutronclient"
NUAGE_DEPENDENCIES = "libvirt perl-JSON lldpad"
NUAGE_VRS_PACKAGE = "nuage-openvswitch nuage-metadata-agent"
VIRT_CUSTOMIZE_MEMSIZE = "2048"
VIRT_CUSTOMIZE_ENV = "export LIBGUESTFS_BACKEND=direct;"

# Gpg values
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
# Function to add RHEL subscription using guestfish
#####


def rhel_subscription(username,
                      password,
                      pool,
                      image,
                      proxy_hostname=None,
                      proxy_port=None):
    subscription_command = ''
    if proxy_hostname is not None:
        proxy_cmd = '''cat <<EOT > rhel_subscription
#!/bin/bash
subscription-manager config --server.proxy_hostname=%s  --server.proxy_port=%s
''' % (proxy_hostname, proxy_port)
        subscription_command = proxy_cmd
    else:
        subscription_command = '''cat <<EOT > rhel_subscription
#!/bin/bash
'''

    enable_pool = '''
subscription-manager register --username=%s --password=%s
subscription-manager attach --pool=%s
subscription-manager repos --enable=rhel-7-server-optional-rpms
subscription-manager repos --enable=rhel-7-server-rpms
EOT''' % (username, password, pool)

    subscription_command = subscription_command + enable_pool
    cmds_run([subscription_command])
    virt_customize_run(
        'rhel_subscription -a %s --memsize %s --selinux-relabel' %
        (image, VIRT_CUSTOMIZE_MEMSIZE))

    cmds_run(['rm -f rhel_subscription'])


#####
# Function to remove the RHEL subscription
#####


def rhel_remove_subscription(image):
    cmds_run([
        '''cat <<EOT > rhel_unsubscribe
#!/bin/bash
subscription-manager unregister
EOT'''
    ])
    virt_customize_run(
        'rhel_unsubscribe -a %s --memsize %s --selinux-relabel' %
        (image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f rhel_unsubscribe'])


#####
# Function to remove packages that are not needed
#####


def uninstall_packages(image):
    virt_customize('"yum remove openvswitch -y" -a %s --memsize %s '
                   '--selinux-relabel' % (image, VIRT_CUSTOMIZE_MEMSIZE))


#####
# Function to install Nuage packages that are required
#####


def install_nuage_packages(image, nuage_vrs_repos):
    enable_repos_cmd = "yum-config-manager --enable"
    for repo in nuage_vrs_repos:
        enable_repos_cmd += " %s" % (repo)
    disable_repos_cmd = enable_repos_cmd.replace("enable", "disable")
    cmds_run([
        '''cat <<EOT > nuage_packages
#!/bin/bash
set -xe
%s
yum install --setopt=skip_missing_names_on_install=False -y %s
yum install --setopt=skip_missing_names_on_install=False -y %s
yum install --setopt=skip_missing_names_on_install=False -y %s
%s
EOT''' % (enable_repos_cmd, NUAGE_DEPENDENCIES, NUAGE_VRS_PACKAGE,
          NUAGE_PACKAGES, disable_repos_cmd)
    ])
    virt_customize_run('nuage_packages -a %s --memsize %s --selinux-relabel' %
                       (image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f nuage_packages'])


#####
# Function to install Nuage AVRS packages that are required
#####


def copy_avrs_packages(image,
                       nuage_avrs_repos):
    enable_repos_cmd = "yum-config-manager --enable"
    for repo in nuage_avrs_repos:
        enable_repos_cmd += " %s" % (repo)
    disable_repos_cmd = enable_repos_cmd.replace("enable", "disable")
    install_cmds = '''cat <<EOT > nuage_avrs_packages
#!/bin/bash
set -xe
%s
mkdir -p /6wind
rm -rf /var/cache/yum/Nuage
yum clean all
touch /kernel-version
rpm -q kernel | awk '{ print substr(\$1,8) }' > /kernel-version
yum install --setopt=skip_missing_names_on_install=False -y createrepo
yum install --setopt=skip_missing_names_on_install=False --downloadonly --downloaddir=/6wind kernel-headers-\$(cat /kernel-version) kernel-devel-\$(cat /kernel-version) kernel-debug-devel-\$(cat /kernel-version) python-pyelftools* dkms* 6windgate* nuage-openvswitch nuage-metadata-agent virtual-accelerator*
yum install --setopt=skip_missing_names_on_install=False --downloadonly --downloaddir=/6wind selinux-policy-nuage-avrs*
yum install --setopt=skip_missing_names_on_install=False --downloadonly --downloaddir=/6wind 6wind-openstack-extensions
rm -rf /kernel-version
yum clean all
%s
EOT''' % (enable_repos_cmd, disable_repos_cmd)
    cmds_run([install_cmds])
    virt_customize_run(
        'nuage_avrs_packages -a %s --memsize %s --selinux-relabel' %
        (image, VIRT_CUSTOMIZE_MEMSIZE))
    cmds_run(['rm -f nuage_avrs_packages'])


#####
# Importing Gpgkeys to Overcloud image
#####


def importing_gpgkeys(image, workingDir, gpgkeys):
    for gpgkey in gpgkeys:
        file_exists = os.path.isfile(gpgkey)
        file_name = os.path.basename(gpgkey)
        if file_exists:
            virt_copy('%s %s /tmp/' % (image, gpgkey))
            virt_customize('"rpm --import /tmp/%s" -a %s --memsize %s '
                           '--selinux-relabel' % (file_name, image,
                                                  VIRT_CUSTOMIZE_MEMSIZE))
        else:
            logger.error("Nuage package signing key is not present in %s ,"
                         "Installation cannot proceed.  Please place the "
                         "signing key in the correct location and retry" %
                         (gpgkey))
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
                     (repofile))
        sys.exit(1)


####
# Image Patching
####


def image_patching(args):
    global GPGCHECK

    if args.logFile:
        handler = logging.FileHandler(args.logFile)
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    workingDir = os.path.dirname(os.path.abspath(__file__))

    if (args.no_signing_key is None) and (args.RpmPublicKey is None):
        logger.error(
            "'--RpmPublicKey' or '--no-signing-key' are not passed in "
            "image patching command, If verification of "
            "Nuage-supplied packages is not required, please restart "
            "image patching with the --no-signing-key option.")
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
        cmds_run([
            'echo "Please install libguestfs-tools-c package '
            'for the script to run"'
        ])
        sys.exit()

    if args.RpmPublicKey:
        cmds_run(['echo "Importing gpgkey(s) to overcloud image"'])
        importing_gpgkeys(args.ImageName, workingDir, args.RpmPublicKey)

    if args.RhelUserName and args.RhelPassword and args.RhelPool:
        cmds_run(['echo "Creating the RHEL subscription"'])
        if args.ProxyHostname and args.ProxyPort:
            rhel_subscription(args.RhelUserName, args.RhelPassword,
                              args.RhelPool, args.ImageName,
                              args.ProxyHostname, args.ProxyPort)
        else:
            rhel_subscription(args.RhelUserName, args.RhelPassword,
                              args.RhelPool, args.ImageName)

    cmds_run(['echo "Uninstalling packages"'])
    uninstall_packages(args.ImageName)

    cmds_run(['echo "Copying RepoFile to the overcloud image"'])
    copy_repo_file(args.ImageName, args.RepoFile)

    if args.AVRSRepoName:
        cmds_run(['echo "Downloading AVRS Packages"'])
        copy_avrs_packages(args.ImageName, args.AVRSRepoName)

    cmds_run(['echo "Installing Nuage Packages"'])
    install_nuage_packages(args.ImageName, args.VRSRepoName)

    if args.RhelUserName and args.RhelPassword and args.RhelPool:
        rhel_remove_subscription(args.ImageName)

    cmds_run(['echo "Done"'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ImageName",
        type=str,
        required=True,
        help="Name of the qcow2 image ("
        "overcloud-full.qcow2 for example)")
    parser.add_argument(
        "--RhelUserName", type=str, help="User name for RHELSubscription")
    parser.add_argument(
        "--RhelPassword", type=str, help="Password for the RHEL Subscription")
    parser.add_argument(
        "--RhelPool", type=str, help="Pool to subscribe to for base packages")
    parser.add_argument(
        "--RepoFile",
        required=True,
        help="Name for the local repo hosting the "
        "Nuage VRS RPMs")
    parser.add_argument(
        "--VRSRepoName",
        action='append',
        help="Name for the local repo hosting the "
        "Nuage VRS RPMs")
    parser.add_argument(
        "--AVRSRepoName",
        action='append',
        help="Name for the local repo hosting the "
        "Nuage AVRS RPMs")
    parser.add_argument(
        "--RpmPublicKey",
        action='append',
        help="RPM GPG Key (repeat option to set "
        "multiple RPM GPG Keys)")
    parser.add_argument(
        "--no-signing-key",
        dest="no_signing_key",
        action="store_true",
        help="Image patching proceeds with package "
        "signature verification disabled")
    parser.add_argument("--ProxyHostname", type=str, help="Proxy Hostname")
    parser.add_argument("--ProxyPort", type=str, help="Proxy Port")
    parser.add_argument(
        "--logFile",
        type=str,
        default='nuage_image_patching.log',
        help="Log file name")
    args = parser.parse_args()
    image_patching(args)


if __name__ == "__main__":
    main()
