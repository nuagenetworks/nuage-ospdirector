Patch diff to /usr/share/openstack-tripleo-heat-templates
----------------------------------------------------------

Version supported:   
openstack-tripleo-heat-templates.noarch 5.2.0-15.el7ost   
overcloud-full-10.0-20170504.2.el7ost.tar

Steps:

1. Download diff_OSPD10_5.2.0-15 from [here](https://github.com/nuagenetworks/nuage-ospdirector/blob/ML2-SRIOV/tripleo-heat-templates-diff/diff_OSPD10_5.2.0-15) to the undercloud machine under /usr/share

2. From /usr/share, run the following command to patch the changes:

   "patch -p0 < diff_OSPD10_5.2.0-15"

3. Verify that all the changes are applied. This should be the output of the command above:

   patching file openstack-tripleo-heat-templates/overcloud-resource-registry-puppet.j2.yaml   
   patching file openstack-tripleo-heat-templates/puppet/extraconfig/pre_deploy/compute/nova-nuage.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/horizon.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-base.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-compute-plugin-nuage.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-ml2-nuage.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-ml2.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-nuage.yaml   
