.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

===================================
Minor Update to Release 6.0.6
===================================

.. contents::
   :local:
   :depth: 3


Use this documentation when updating between nuage minor releases. The process applies to updates from Release 6.0.5 to Release 6.0.6. During this process, the Nuage components are updated to 6.0.6.

Note:  Nuage 6.0.6 release is supported with RHEL 7.7. Please make sure Red Hat packages are not updated to newer versions during the Nuage minor update process.

It is assumed the operator is familiar with Red Hat OpenStack Platform Director updates, VSP installation, the distribution-specific installation and update practices, and the specific requirements for operations in a production environment.


Update Paths
-------------

In this release, you can update only from OSP Director 13 + 6.0.5 to OSP Director 13 + 6.0.6.


These update paths are not described in this document:

    * Update from OpenStack releases before Queens 6.0.5
    * Update from VSP releases before Release 6.0.5


Basic Configuration
---------------------

The basic configuration includes:

   * One or more Controller node(s)
   * One or more Compute nodes (hypervisors) running the VRS, SR-IOV, AVRS or OVRS nodes running Release 6.0.5



Before the Update
--------------------

1. If you are updating an AVRS node, migrate all your VMs on the node to an AVRS Compute node that is not being updated. Perform the steps in the "Live Migrate a Virtual Machine" section in https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/migrating-virtual-machines-between-compute-nodes-osp#live-migrate-a-vm-osp

2. Create a single repositories containing 6.0.6 Nuage SR-IOV packages and 6.0.5 for remaining all nuage packages. Enable this repository on all overcloud nodes. The repository contents may change depending on the roles configured for your deployment.

    ::

       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Group          | Packages                                     | Location (tar.gz or link)                                                                 |
       +================+==============================================+===========================================================================================+
       |                | nuage-bgp                                    | nuage-vrs-el7 or nuage-avrs-el7                                                           |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Nuage          | nuage-openstack-neutronclient                | nuage-openstack                                                                           |
       | Common         +----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Packages       | nuage-puppet-modules-6.2.0                   | https://github.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/nuage-puppet-modules       |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | nuage-metadata-agent                         | nuage-vrs-el7 or nuage-avrs-el7                                                           |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | python-openswitch-nuage                      | nuage-vrs-el7 or nuage-avrs-el7                                                           |
       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Nuage VRS      | nuage-openvswitch                            | nuage-vrs-el7                                                                             |
       | Packages       +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | selinux-policy-nuage                         | nuage-selinux                                                                             |
       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Offload        | nuage-openvswitch-ovrs                       | Contact Nuage Networks for more information about this package.                           |
       | VRS (OVRS)     +----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Packages       | mstflint                                     | rhel-7-server-rpms                                                                        |                                                                             |
       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-dpdk                               | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Accelerated    | 6windgate-dpdk-pmd-mellanox-rdma-core        | nuage-avrs-el7                                                                            |
       | VRS (AVRS)     +----------------------------------------------+-------------------------------------------------------------------------------------------+
       | 6WIND          | 6windgate-dpdk-pmd-virtio-host               | nuage-avrs-el7                                                                            |
       | Packages       +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-fp                                 | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-fp-ovs                             | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-fpn-sdk-dpdk                       | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-linux-fp-sync                      | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-linux-fp-sync-fptun                | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-linux-fp-sync-ovs                  | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-linux-fp-sync-vrf                  | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-product-base                       | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-tools-common-libs-daemonctl        | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-tools-common-libs-libconsole       | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | 6windgate-tools-common-libs-pyroute2         | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | dkms                                         | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | nuage-openvswitch-6wind                      | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | python-pyelftools                            | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | virtual-accelerator-base                     | nuage-avrs-el7                                                                            |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | selinux-policy-nuage-avrs                    | nuage-avrs-selinux                                                                        |
       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Nuage SR-IOV   | nuage-topology-collector (for Nuage SR-IOV)  | nuage-openstack                                                                           |
       | packages       |                                              |                                                                                           |
       |                |                                              |                                                                                           |
       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+


3. Please make sure only nuage 6.0.6 repo is enabled and remaining all repos are disabled on all overcloud nodes for this update.

.. Note:: During our update testing, where overcloud nodes are subscribed to Red Hat Subscription since fresh deployment i.e using `openstack overcloud deploy` command, we had to set `rhel_reg_force: false` inside `environment-rhel-registration.yaml`. This way the repolist on overcloud nodes that is done in step-3 won't be changed during update.


4. Please run "yum clean all" to clean the old yum cache on all your overcloud nodes after enabling above yum repositories.


Update Overview
----------------

As part of this update, we are providing instructions to update Nuage containers on overcloud nodes from 6.0.5 to 6.0.6.
All the packages on overcloud nodes will still remain at 6.0.5.
Once the update is complete, users won't need to patch overcloud image again.
Already existing overcloud image can be used along with the 6.0.6 Nuage containers for scale outs.


Update Workflow
------------------

1. Back up the configuration files for your deployment.

     In the following example, all the templates and environment files for your deployment are in the /home/stack/nuage-ospdirector directory. To get new the Nuage 6.0.6 nuage-ospdirector/nuage-tripleoheat-templates, back up the files before replacing the existing ones with new 6.0.6 codebase.

    a. Back up the templates and environment files from /home/stack/nuage-ospdirector to /home/stack/nuage-ospdirector-bk.

       ::

           $ mv /home/stack/nuage-ospdirector /home/stack/nuage-ospdirector-bk


    b. Get the tar files for the update one of these ways:

       * Download them from https://github.com/nuagenetworks/nuage-ospdirector/releases
       * Use ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b <release>``. For example, enter ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b 13.606.1``.


    c. Copy the nuage-tripleo-heat-templates folder from /home/stack/nuage-ospdirector-osp-13.<release>/nuage-tripleo-heat-templates to /home/stack/ directory on undercloud.

        ::

            $ cd /home/stack
            $ ln -s nuage-ospdirector/nuage-tripleo-heat-templates .


2. Regenerate roles data file by following below instructions

    a. Copy the roles from /usr/share/openstack-tripleo-heat-templates/roles to /home/stack/nuage-tripleo-heat-templates/roles

        ::

            $ cp /usr/share/openstack-tripleo-heat-templates/roles/* /home/stack/nuage-tripleo-heat-templates/roles/

    b. Run create_all_roles.sh to generate Nuage compute roles

        ::

            $ cd home/stack/nuage-tripleo-heat-templates/scripts/create_roles/
            $ ./create_all_roles.sh

    c. Create a *nuage_roles_data.yaml* file with all the required roles for the current Overcloud deployment.
       This example shows how to create *nuage_roles_data.yaml* with a Controller and Compute nodes for VRS, AVRS, OVRS, and SR-IOV. The respective roles are specified in the same order. The following example has the respective role names mentioned in the same order.

        ::

            Syntax:
            openstack overcloud roles generate --roles-path /home/stack/nuage-tripleo-heat-templates/roles -o /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml Controller Compute <role> <role> ...

            Example:
            openstack overcloud roles generate --roles-path /home/stack/nuage-tripleo-heat-templates/roles -o /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml Controller Compute ComputeAvrs ComputeOvrs ComputeSriov


        .. Note:: It is not mandatory to create nuage_roles_data.yaml with all the roles shown in the example. You can specify only the required ones for your deployment.


3. Make sure your all of the templates and environment files are updated with the environment values for your deployment.

    a. Get the environment values from the /home/stack/nuage-ospdirector-bk directory and update all the templates and environment files for the deployment, such as neutron-nuage/nova-nuage/compute-avrs/ovs-hw-offload/mellanox-environment.

    b. Make sure `NeutronPluginExtensions` options in neutron-nuage-config.yaml contains `nuage_network`, which is added in 6.0.6:

        ::

            NeutronPluginExtensions: 'nuage_network,nuage_subnet,nuage_port,port_security'


4. Get the latest Nuage docker images from the Red Hat Partner Registry by following these instructions in Phase 3.2. Nuage Docker Containers from `6.0/README.rst <../../README.rst>`_


5. To update the Overcloud deployment, follow these instructions: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/assembly-updating_the_overcloud


6. Once the overcloud update is complete, enable nuage 6.0.6 repo on undercloud and update nuage-topology-collector using:

    ::

        $ sudo yum update nuage-topology-collector -y




