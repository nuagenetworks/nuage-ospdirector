#!/usr/bin/python


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

# Functionality to compare the installed openstack-tripleo-heat-templates
# version with the available diff versions and patch the appropriate diff.
# Since different openstack-tripleo-heat-templates can require different
# diff patches to be applied, this functionality takes care of hiding
# those details while applying the right patch. Currently all versions
# upto version openstack-tripleo-heat-templates-8.0.7-21 are handled.
# Later versions are not supported at this time.
#
# Usage: sudo ./apply_patch.py or sudo python apply_patch.py
# Usage for AVRS Integration: sudo ./apply_patch.py avrs or sudo python apply_patch.py avrs
#

import os
import rpm
import sys
import subprocess
from rpmUtils.miscutils import stringToVersion
import constants



def get_dirpath():
    dirpath = os.path.dirname(os.path.abspath(__file__))
    return dirpath

def is_supported_feature(feature):
    if feature in constants.SUPPORTED_FEATURES:
        return True
    return False

def version_compare((e1, v1, r1), (e2, v2, r2)):
    return rpm.labelCompare((e1, v1, r1), (e2, v2, r2))


def file_exists(filename):
    if not os.path.exists(filename):
        print "File: %s is not present in the current directory. " \
              "Please check!!" % filename
        sys.exit(1)
    return filename

def apply_patch(diff_version, features):

    try:
        dirpath = get_dirpath() + '/'
        for feature in features:
            diff_file_path = dirpath + feature + '/' + \
                             constants.DIFF + feature + '_' + diff_version
            file_exists(diff_file_path)
            args = constants.PATCH_COMMAND + diff_file_path
            print "Applying %s diff" % feature
            subprocess.call(args, shell=True)
    except Exception as e:
        print "Failed while applying patching with error %s " % e
        sys.exit(1)

def main():
    enable_features = []
    if len(sys.argv) < 1:
        print "Usage: %s" % sys.argv[0]
        sys.exit(1)
    elif len(sys.argv) > 1:
        enable_features = sys.argv[1:]
        for feature in enable_features:
            if not is_supported_feature(feature):
                print "Error: %s is not supported feature \n" % feature
                print "Please refer README.md"
                sys.exit(1)

    enable_features += constants.COMMON_PATCH

    version = subprocess.check_output(
        ['rpm', '-qa', 'openstack-tripleo-heat-templates']
    )

    if not version:
        print "ERROR: Make sure openstack-tripleo-heat-templates" \
              " package is installed before running this script"
        sys.exit(1)

    (e0, v0, r0) = stringToVersion(version)
    (e1, v1, r1) = stringToVersion(constants.VERSION_1_CHECK)
    (e2, v2, r2) = stringToVersion(constants.VERSION_2_CHECK)
    (e3, v3, r3) = stringToVersion(constants.VERSION_3_CHECK)
    (e4, v4, r4) = stringToVersion(constants.VERSION_4_CHECK)

    

    # Compare versions
    version_1_rc = version_compare((e0, v0, r0), (e1, v1, r1))
    version_2_rc = version_compare((e0, v0, r0), (e2, v2, r2))
    version_3_rc = version_compare((e0, v0, r0), (e3, v3, r3))
    version_4_rc = version_compare((e0, v0, r0), (e4, v4, r4))

    if version_1_rc <= 0:
        diff_version = constants.VERSION_1_DIFF

    elif version_1_rc > 0 and version_2_rc <= 0:
        diff_version = constants.VERSION_2_DIFF

    elif version_2_rc > 0 and version_3_rc <= 0:
        diff_version = constants.VERSION_3_DIFF

    elif version_3_rc > 0 and version_4_rc <= 0:
        diff_version = constants.VERSION_4_DIFF

    elif version_4_rc > 0:
        print "Not supported for %s" % version
        sys.exit(1)

    # Apply appropriate diff

    apply_patch(diff_version, enable_features)


if __name__ == '__main__':
    main()
