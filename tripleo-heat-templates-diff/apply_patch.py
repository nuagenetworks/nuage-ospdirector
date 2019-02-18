#!/usr/bin/python

##############################################################################
# Copyright Nokia 2018
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
#

import os
import rpm
import sys
import subprocess
from rpmUtils.miscutils import stringToVersion

VERSION_1_CHECK = "openstack-tripleo-heat-templates-8.0.2-4.el7ost.noarch"
VERSION_2_CHECK = "openstack-tripleo-heat-templates-8.0.2-43.el7ost.noarch"
VERSION_3_CHECK = "openstack-tripleo-heat-templates-8.0.7-4.el7ost.noarch"
VERSION_4_CHECK = "openstack-tripleo-heat-templates-8.0.7-21.el7ost.noarch"
PRE_VERSION_1_DIFF = "diff_OSPD13_8.0.2-4"
VERSION_2_DIFF = "diff_OSPD13_8.0.2-43"
VERSION_3_DIFF = "diff_OSPD13_8.0.7-4"
VERSION_4_DIFF = "diff_OSPD13_8.0.7-21"


def version_compare((e1, v1, r1), (e2, v2, r2)):
    return rpm.labelCompare((e1, v1, r1), (e2, v2, r2))


def file_exists(filename):
    if not os.path.exists(filename):
        print "File: %s is not present in the current directory. " \
              "Please check!!" % filename
        sys.exit(1)
    return filename


def main():

    if len(sys.argv) != 1:
        print "Usage: %s" % sys.argv[0]
        sys.exit(1)

    version = subprocess.check_output(
        ['rpm', '-qa', 'openstack-tripleo-heat-templates']
    )

    if not version:
        print "ERROR: Make sure openstack-tripleo-heat-templates" \
              " package is installed before running this script"
        sys.exit(1)

    else:

        (e0, v0, r0) = stringToVersion(version)
        (e1, v1, r1) = stringToVersion(VERSION_1_CHECK)
        (e2, v2, r2) = stringToVersion(VERSION_2_CHECK)
        (e3, v3, r3) = stringToVersion(VERSION_3_CHECK)
        (e4, v4, r4) = stringToVersion(VERSION_4_CHECK)

        args = "patch -p0 -N -d /usr/share"

        # Compare versions
        version_1_rc = version_compare((e0, v0, r0), (e1, v1, r1))
        version_2_rc = version_compare((e0, v0, r0), (e2, v2, r2))
        version_3_rc = version_compare((e0, v0, r0), (e3, v3, r3))
        version_4_rc = version_compare((e0, v0, r0), (e4, v4, r4))

        if version_1_rc <= 0:
            args = args + " < " + file_exists(PRE_VERSION_1_DIFF)

        elif version_1_rc > 0 and version_2_rc <= 0:
            args = args + " < " + file_exists(VERSION_2_DIFF)

        elif version_2_rc > 0 and version_3_rc <= 0:
            args = args + " < " + file_exists(VERSION_3_DIFF)

        elif version_3_rc > 0 and version_4_rc <= 0:
            args = args + " < " + file_exists(VERSION_4_DIFF)

        elif version_4_rc > 0:
            print "Not supported for %s" % version
            sys.exit(1)

        # Apply appropriate diff
        print "Applying: %s" % args
        try:
            subprocess.call(args, shell=True)
        except Exception as e:
            print "Failed while applying patching with error %s " % e
            sys.exit(1)

        return


if __name__ == '__main__':
    main()
