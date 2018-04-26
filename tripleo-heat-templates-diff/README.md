Steps:

Download the three diff files and apply_patch.py script from here to the undercloud machine

Run the following command to patch the changes:

"./apply_patch.py"

Verify that all the changes are applied. Ensure that there are no "Hunk #1 FAILED" errors. There might be "hunk ignored" warnings (based on running version) which can be ignored.

Version supported by the script: openstack-tripleo-heat-templates-8.0.2-0.20180327213843.f25e2d8.el7ost.noarch
