Patch diff to /usr/share/openstack-tripleo-heat-templates
----------------------------------------------------------

Version supported:   

OSPD 12:

openstack-tripleo-heat-templates.noarch 7.0.3-22.el7ost   
overcloud-full-12.0-20180126.1.el7ost.tar

Steps:

1. Download the appropriate diff file from [here](https://github.com/nuagenetworks/nuage-ospdirector/blob/ML2-SRIOV/tripleo-heat-templates-diff/) to the undercloud machine under /usr/share

2. From /usr/share, run the following command to patch the changes:

   "patch -p0 < <diff_file_name>"

3. Verify that all the changes are applied.   
