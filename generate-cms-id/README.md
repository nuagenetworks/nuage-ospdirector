##############################################################################
# Copyright 2015 Alcatel-Lucent USA Inc.
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

GENERATE CMS ID
----------------

Steps:

1. Copy the folder to a machine that can reach VSD (typically the undercloud node)

2. From the folder run the following command to generate CMS\_ID:

   "python configure\_vsd\_cms\_id.py --server <vsd-ip-address>:<vsd-port> --serverauth <vsd-username>:<vsd-password> --organization <vsd-organization> --auth\_resource /me --serverssl True --base\_uri /nuage/api/<vsp-version>"

   example command : 
     "python configure_vsd_cms_id.py --server 0.0.0.0:0 --serverauth username:password --organization organization --auth_resource /me --serverssl True --base_uri /nuage/api/v3_2"

3. The CMS ID will be displayed on the terminal as well as a copy of it will be stored in a file "cms\_id.txt" in the same folder.
