##############################################################################
# Copyright Nokia 2019
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################

VERSION_1_CHECK = "openstack-tripleo-heat-templates-8.0.2-4.el7ost.noarch"
VERSION_2_CHECK = "openstack-tripleo-heat-templates-8.0.2-43.el7ost.noarch"
VERSION_3_CHECK = "openstack-tripleo-heat-templates-8.0.7-4.el7ost.noarch"
VERSION_4_CHECK = "openstack-tripleo-heat-templates-8.0.7-21.el7ost.noarch"
VERSION_1_DIFF = "8.0.2-4"
VERSION_2_DIFF = "8.0.2-43"
VERSION_3_DIFF = "8.0.7-4"
VERSION_4_DIFF = "8.0.7-21"
DIFF = 'diff_'

SUPPORTED_FEATURES = ['avrs']
COMMON_PATCH = ["common"]

PATCH_COMMAND = "patch -p0 -N -d /usr/share < "