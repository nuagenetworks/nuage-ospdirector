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
# == Class: nova:testing::config
#
# This class is aim to configure nova.testing parameters
#
# === Parameters:
#
# [*monkey_patch*]
#   (optional) Apply monkey patching or not
#   Defaults to false
#
# [*monkey_patch_modules*]
#   (optional) List of modules/decorators to monkey patch
#   Defaults to undef
#
class nova::patch::config (
  $monkey_patch                        = false,
  $monkey_patch_modules                = $::os_service_default,
) {

  include ::nova::deps

  $monkey_patch_modules_real = pick(join(any2array($monkey_patch_modules), ','), $::os_service_default)

  nova_config {
    'DEFAULT/monkey_patch':         value => $monkey_patch;
    'DEFAULT/monkey_patch_modules': value => $monkey_patch_modules_real;
  }
}
