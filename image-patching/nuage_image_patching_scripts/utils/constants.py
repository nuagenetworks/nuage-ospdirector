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

# List of Nuage packages
NUAGE_PYTHON_OVS = "python-openvswitch-nuage"
NUAGE_AVRS_PACKAGE = "nuage-openvswitch-6wind"
NUAGE_PACKAGES = "nuage-puppet-modules " \
                 "nuage-openstack-neutronclient " \
                 "selinux-policy-nuage nuage-bgp"
NUAGE_DEPENDENCIES = "python2 perl-JSON lldpad python3-httplib2 " \
                     "libvirt mstflint"

NUAGE_VRS_PACKAGE = "nuage-openvswitch nuage-metadata-agent"
VIRT_CUSTOMIZE_MEMSIZE = "2048"
VIRT_CUSTOMIZE_ENV = "export LIBGUESTFS_BACKEND=direct;"
PATCHING_SCRIPT = ''
SCRIPT_NAME = 'patching_script.sh'
TEMPORARY_PATH = '/tmp/'
LOG_FILE_NAME = 'nuage_image_patching.log'
VALID_DEPLOYMENT_TYPES = ['vrs', 'avrs']
RHEL_SUB_PORTAL = "portal"
RHEL_SUB_SATELLITE = "satellite"
RHEL_SUB_DISABLED = "disabled"
