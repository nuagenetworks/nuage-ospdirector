Steps:

Download the three diff files and apply_patch.py script from here to the undercloud machine

Run the following command to patch the changes:

"python apply_patch.py"

Verify that all the changes are applied. Ensure that there are no "Hunk #1 FAILED" errors. There might be "hunk ignored" warnings (based on running version) which can be ignored.

Multiple versions are supported by the script: openstack-tripleo-heat-templates-8.0.2-4.el7ost.noarch, openstack-tripleo-heat-templates-8.0.2-43.el7ost.noarch, openstack-tripleo-heat-templates-8.0.4-20.el7ost.noarch and openstack-tripleo-heat-templates-8.0.7-4.el7ost.noarch

