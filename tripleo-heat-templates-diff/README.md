Patch diff to /usr/share/openstack-tripleo-heat-templates
----------------------------------------------------------

Steps:

Download the three diff files and apply_patch.py script from [here](https://github.com/nuagenetworks/nuage-ospdirector/tree/OSPD12/tripleo-heat-templates-diff) to the undercloud machine

Run the following command to patch the changes:

"sudo python apply_patch.py"

Verify that all the changes are applied. Ensure that there are no "Hunk #1 FAILED" errors.
There might be "hunk ignored" warnings (based on running version) which can be ignored.

Multiple versions are supported by the script:
openstack-tripleo-heat-templates-7.0.3-18.el7ost.noarch, openstack-tripleo-heat-templates-7.0.3-22.el7ost.noarch and openstack-tripleo-heat-templates-7.0.9-8.el7ost.noarch
