#!/bin/bash
#
# This script is used to patch an existing OpenStack
# image with Nuage components
#
# This script takes in following input parameters:
# RepoName    : Name of the local repository
# RepoBaseUrl : Base URL of the local repository
# Version     : Version of OSP Director (7 or 8)
# ImageName   : Name of qcow2 image to patch
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
NUAGE_PACKAGES="nuage-openstack-neutron nuagenetlib nuage-openstack-neutronclient nuage-metadata-agent nuage-puppet-modules nuage-openstack-heat nuage-openstack-horizon"
NUAGE_DEPENDENCIES="libvirt python-twisted-core perl-JSON qemu-kvm vconfig python-novaclient"
NUAGE_VRS_PACKAGE="nuage-openvswitch"
VIRT_CUSTOMIZE_MEMSIZE="2048"


###
CONTINUE_SCRIPT=true

#####
# Function to print help message
#####

function show_help {

echo "Options are"
echo " --ImageName= Name of the qcow2 image (overcloud-full.qcow2 for example)"
echo " --RepoName=Name for the local repo hosting the Nuage RPMs"
echo " --RepoBaseUrl=Base URL for the repo hosting the Nuage RPMs"
echo " --Version=OSP-Director version (7, 8 or 9)?"
echo " -h or --help: Show this message"
}

#####
# Function to add files based on the version
#####

function add_files {

if [ $2 -eq 7 ]; then
  virt-customize --run-command 'mkdir -p /etc/puppet/modules/nuage/manifests/7_files' -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'

  virt-copy-in -a $1 7_files/neutron_plugin_nuage.rb /etc/puppet/modules/nuage/manifests/7_files
  virt-copy-in -a $1 7_files/impl_ifcfg.py /etc/puppet/modules/nuage/manifests/7_files
  virt-copy-in -a $1 7_files/ini_setting.rb /etc/puppet/modules/nuage/manifests/7_files

  virt-customize --run-command 'cp /etc/puppet/modules/nuage/manifests/7_files/neutron_plugin_nuage.rb /etc/puppet/modules/neutron/lib/puppet/type/neutron_plugin_nuage.rb' -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'
  virt-customize --run-command 'cp /etc/puppet/modules/nuage/manifests/7_files/ini_setting.rb /etc/puppet/modules/neutron/lib/puppet/provider/neutron_plugin_nuage/ini_setting.rb' -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'
  virt-customize --run-command 'cp /etc/puppet/modules/nuage/manifests/7_files/impl_ifcfg.py /usr/lib/python2.7/site-packages/os_net_config/impl_ifcfg.py' -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'

fi

if [ $2 -eq 8 ]; then

  virt-customize --run-command 'mkdir -p /etc/puppet/modules/nuage/manifests/8_files' -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'

  virt-copy-in -a $1 8_files/neutron_plugin_nuage.rb /etc/puppet/modules/nuage/manifests/8_files

  virt-customize --run-command 'cp /etc/puppet/modules/nuage/manifests/8_files/neutron_plugin_nuage.rb /etc/puppet/modules/neutron/lib/puppet/type/neutron_plugin_nuage.rb' -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'

fi

if [ $2 -eq 9 ]; then
  :
fi

}


#####
# Function to remove packages that are not needed
#####

function uninstall_packages {

# For Newton and above, use standard python-openvswitch
if [ $2 -le 9 ]; then
  virt-customize --run-command 'yum remove python-openvswitch -y' -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'
fi

virt-customize --run-command 'yum remove openvswitch -y' -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'

}

#####
# Function to install Nuage packages that are required
#####

function install_packages {

cat <<EOT >> nuage_packages
yum install $NUAGE_DEPENDENCIES -y
yum install $NUAGE_PACKAGES -y
EOT

virt-customize --run nuage_packages -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'

rm -f nuage_packages
}

#####
# Installing VRS and the dependencies for VRS
#####

function install_vrs {

cat <<EOT >> vrs_packages
yum install $NUAGE_VRS_PACKAGE -y
EOT

virt-customize --run vrs_packages -a $1 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'

rm -f vrs_packages

}




#####
# Function to create the repo file
#####

function create_repo_file {

cat <<EOT >> create_repo
touch /etc/yum.repos.d/nuage.repo
echo "[Nuage]" >> /etc/yum.repos.d/nuage.repo
echo "name=$1" >> /etc/yum.repos.d/nuage.repo
echo "baseurl=$2" >> /etc/yum.repos.d/nuage.repo
echo "enabled = 1" >> /etc/yum.repos.d/nuage.repo
echo "gpgcheck = 0" >> /etc/yum.repos.d/nuage.repo
EOT

virt-customize --run create_repo -a $3 --memsize $VIRT_CUSTOMIZE_MEMSIZE --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'

}


#####
# Function to clean up the repo file
#####
function delete_repo_file {

virt-customize --run-command "rm -f /etc/yum.repos.d/nuage.repo" -a $1 --selinux-relabel --edit '/usr/lib/systemd/system/rhel-autorelabel.service: $_ = "" if /StandardInput=tty/'
rm -f create_repo
}

if [ $# -lt 4 ]; then
  CONTINUE_SCRIPT=false
  show_help
fi

for i in "$@"
do
case $i in
    --ImageName=*)
    ImageName="${i#*=}"
    ;;
    --RepoName=*)
    RepoName="${i#*=}"
    ;;
    --RepoBaseUrl=*)
    RepoBaseUrl="${i#*=}"
    ;;
    --Version=*)
    Version="${i#*=}"
    ;;
    -h|--help)
    show_help
    CONTINUE_SCRIPT=false
    return
    ;;
    *)
    echo "unknown option"
    show_help        # unknown option
    CONTINUE_SCRIPT=false
    return
    ;;
esac
done


if [ "$CONTINUE_SCRIPT" = true ]; then

    echo "Verifying pre-requisite packages for script"
    if ! rpm -q --quiet libguestfs-tools-c ; then
        echo "Please install libguestfs-tools-c package for the script to run"
        return
    fi

    echo "Uninstalling packages"

    uninstall_packages $ImageName $Version

    echo "Creating Repo File"

    create_repo_file $RepoName $RepoBaseUrl $ImageName

    echo "Installing Nuage Packages"

    install_packages $ImageName

    echo "Installing VRS"

    install_vrs $ImageName

    echo "Cleaning up"

    delete_repo_file $ImageName

    echo "Adding files post-patching"

    add_files $ImageName $Version

    echo "Done"

fi
