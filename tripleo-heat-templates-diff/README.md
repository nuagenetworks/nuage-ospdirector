Patch diff to /usr/share/openstack-tripleo-heat-templates
----------------------------------------------------------

Version supported:   
openstack-tripleo-heat-templates.noarch 5.2.0-15.el7ost   
overcloud-full-10.0-20170504.2.el7ost.tar

Steps:

1. Download diff_OSPD10 from [here](https://github.com/nuagenetworks/nuage-ospdirector/blob/ML2-SRIOV-VZ/tripleo-heat-templates-diff/diff_OSPD10) to the undercloud machine under /usr/share

2. From /usr/share, run the following command to patch the changes:

   "patch -p0 -N < diff\_OSPD10"

3. Verify that all the changes are applied. This should be the output of the command above:

   patching file openstack-tripleo-heat-templates/overcloud-resource-registry-puppet.j2.yaml   
   patching file openstack-tripleo-heat-templates/puppet/extraconfig/pre_deploy/compute/nova-nuage.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/horizon.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-base.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-compute-plugin-nuage.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-ml2-nuage.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-ml2.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-nuage.yaml   


Version supported:   
openstack-tripleo-heat-templates-5.3.0-4.el7ost.noarch and openstack-tripleo-heat-templates-5.3.0-6.el7ost.noarch    
overcloud-full-10.0-20170504.2.el7ost.tar

Steps:

1. Download diff_OSPD10 from [here](https://github.com/nuagenetworks/nuage-ospdirector/blob/ML2-SRIOV-VZ/tripleo-heat-templates-diff/diff_OSPD10) to the undercloud machine under /usr/share

2. From /usr/share, run the following command to patch the changes:

   "patch -p0 -N < diff\_OSPD10"

3. Some changes from the diff_patch are already included. "-N" option will skip over them. Verify that rest of the changes are applied. This should be the output of the command above:

   patching file openstack-tripleo-heat-templates/overcloud-resource-registry-puppet.j2.yaml   
   Hunk #1 succeeded at 144 (offset 3 lines).   
   patching file openstack-tripleo-heat-templates/puppet/extraconfig/pre_deploy/compute/nova-nuage.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/horizon.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-base.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-compute-plugin-nuage.yaml   
   Reversed (or previously applied) patch detected!  Skipping patch.   
   2 out of 2 hunks ignored -- saving rejects to file openstack-tripleo-heat-templates/puppet/services/neutron-compute-plugin-nuage.yaml.rej   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-ml2-nuage.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-ml2.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-nuage.yaml   
   Reversed (or previously applied) patch detected!  Skipping patch.   
   2 out of 2 hunks ignored -- saving rejects to file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-nuage.yaml.rej   


Version supported:   
openstack-tripleo-heat-templates-5.3.3-1.el7ost.noarch.rpm

Steps:

1. Download diff_OSPD10 from [here](https://github.com/nuagenetworks/nuage-ospdirector/blob/ML2-SRIOV-VZ/tripleo-heat-templates-diff/diff_OSPD10) to the undercloud machine under /usr/share

2. From /usr/share, run the following command to patch the changes:

   "patch -p0 -N < diff\_OSPD10"

3. Some changes from the diff_patch are already included. "-N" option will skip over them. Verify that rest of the changes are applied. This should be the output of the command above:

   patching file openstack-tripleo-heat-templates/overcloud-resource-registry-puppet.j2.yaml   
   Reversed (or previously applied) patch detected!  Skipping patch.   
   1 out of 1 hunk ignored -- saving rejects to file openstack-tripleo-heat-templates/overcloud-resource-registry-puppet.j2.yaml.rej   
   patching file openstack-tripleo-heat-templates/puppet/extraconfig/pre_deploy/compute/nova-nuage.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/horizon.yaml   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-base.yaml   
   Reversed (or previously applied) patch detected!  Skipping patch.   
   2 out of 2 hunks ignored -- saving rejects to file openstack-tripleo-heat-templates/puppet/services/neutron-base.yaml.rej   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-compute-plugin-nuage.yaml   
   Reversed (or previously applied) patch detected!  Skipping patch.   
   2 out of 2 hunks ignored -- saving rejects to file openstack-tripleo-heat-templates/puppet/services/neutron-compute-plugin-nuage.yaml.rej   
   The next patch would create the file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-ml2-nuage.yaml,   
   which already exists!  Skipping patch.   
   1 out of 1 hunk ignored   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-ml2.yaml   
   Reversed (or previously applied) patch detected!  Skipping patch.   
   1 out of 1 hunk ignored -- saving rejects to file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-ml2.yaml.rej   
   patching file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-nuage.yaml   
   Reversed (or previously applied) patch detected!  Skipping patch.   
   2 out of 2 hunks ignored -- saving rejects to file openstack-tripleo-heat-templates/puppet/services/neutron-plugin-nuage.yaml.rej   
