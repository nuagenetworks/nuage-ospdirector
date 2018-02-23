Patch diff to /usr/share/openstack-tripleo-heat-templates
----------------------------------------------------------

Version supported:   

OSPD 10:

openstack-tripleo-heat-templates.noarch 5.2.0-15.el7ost   
overcloud-full-10.0-20170504.2.el7ost.tar

OSPD 11:

openstack-tripleo-heat-templates.noarch 6.2.0-3.el7ost   
overcloud-full-11.0-20170630.1.el7ost.tar

OSPD 12:

openstack-tripleo-heat-templates.noarch 7.0.3-22.el7ost
overcloud-full-12.0-20180126.1.el7ost.tar

Steps:

1. Download the appropriate diff file from [here](https://github.com/nuagenetworks/nuage-ospdirector/blob/ML2-SRIOV/tripleo-heat-templates-diff/) to the undercloud machine under /usr/share

2. From /usr/share, run the following command to patch the changes:

   "patch -p0 < <diff_file_name>"

3. Verify that all the changes are applied.   
