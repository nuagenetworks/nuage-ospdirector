#!/usr/bin/python

# Functionality to compare the installed openstack-tripleo-heat-templates
# version with the available diff versions and patch the appropriate diff.
# Since different openstack-tripleo-heat-templates can require different
# diff patches to be applied, this functionality takes care of hiding
# those details while applying the right patch. Currently all versions
# upto version openstack-tripleo-heat-templates-8.0.2-14 are handled.
# Later versions are not supported at this time.
#
# Usage: ./apply_patch.py
#

import rpm
import sys
import subprocess
from rpmUtils.miscutils import stringToVersion

VERSION_1_CHECK = "openstack-tripleo-heat-templates-8.0.2-4.el7ost.noarch"
VERSION_2_CHECK = "openstack-tripleo-heat-templates-8.0.2-14.el7ost.noarch"
PRE_VERSION_1_DIFF = "diff_OSPD13_8.0.2-4"
VERSION_2_DIFF = "diff_OSPD13_8.0.2-14"


if len(sys.argv) != 1:
    print "Usage: %s" % sys.argv[0]
    sys.exit(1)

def version_compare((e1, v1, r1), (e2, v2, r2)):
    return rpm.labelCompare((e1, v1, r1), (e2, v2, r2))

version = subprocess.check_output(['rpm', '-qa', 'openstack-tripleo-heat-templates'])

(e0, v0, r0) = stringToVersion(version)
(e1, v1, r1) = stringToVersion(VERSION_1_CHECK)
(e2, v2, r2) = stringToVersion(VERSION_2_CHECK)

args = "patch -p0 -N -d /usr/share"

# Compare versions
version_1_rc = version_compare((e0, v0, r0), (e1, v1, r1))

if version_1_rc <= 0:
    args = args + " < " + PRE_VERSION_1_DIFF

elif version_1_rc > 0 and version_2_rc <= 0:
    args = args + " < " + PRE_VERSION_2_DIFF

elif version_2_rc > 0:
    print "Not supported for %s" % version
    sys.exit(1)

# Apply appropriate diff
print "Applying: %s" % args
subprocess.call(args, shell=True)
