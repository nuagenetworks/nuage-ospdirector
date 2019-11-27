# List of Nuage packages
NUAGE_PYTHON_OVS = "python-openvswitch-nuage"
NUAGE_AVRS_PACKAGE = "nuage-openvswitch-6wind"
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
LOG_FILE_NAME='nuage_image_patching.log'
