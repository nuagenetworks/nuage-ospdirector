Patch diff to /usr/share/openstack-tripleo-heat-templates
----------------------------------------------------------

Steps:   

1. Download the four diff files and apply_patch.py script from [here](https://github.com/nuagenetworks/nuage-ospdirector/blob/OSPD10/tripleo-heat-templates-diff/) to the undercloud machine   

2. Run the following command to patch the changes:   

   "sudo python apply_patch.py"   

   Verify that all the changes are applied. Ensure that there are no "Hunk #1 FAILED" errors.   
   There might be "hunk ignored" warnings (based on running version) which can be ignored.   

Multiple versions are supported by the script:   
openstack-tripleo-heat-templates.noarch 5.2.0-15.el7ost, 5.2.0-20.el7ost, 5.2.0-21.el7ost and 5.2.0-25.el7ost   
openstack-tripleo-heat-templates-5.3.0-4.el7ost.noarch and openstack-tripleo-heat-templates-5.3.0-6.el7ost.noarch   
openstack-tripleo-heat-templates-5.3.3-1.el7ost.noarch and openstack-tripleo-heat-templates-5.3.8-1.el7ost.noarch   
openstack-tripleo-heat-templates-5.3.10-1.el7ost.noarch and openstack-tripleo-heat-templates-5.3.10-23.el7ost.noarch
