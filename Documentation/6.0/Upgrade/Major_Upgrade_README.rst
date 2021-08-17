.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

===================================
Major Upgrade to Release 6.0.17
===================================

.. contents::
   :local:
   :depth: 3


Use this documentation when upgrading between major Nuage releases. The process applies to updates from Release 5.4.1 U17 (Z12) to Release 6.0.17 (Z16). During this process:

 1. Nuage components are updated to 6.0.17.
 2. Red Hat OpenStack is updated to Z16.

Note:  Nuage 6.0.17 release is supported with RHEL 7.9. Make sure the Red Hat packages are updated to the Z16 stream during the major Nuage update process.

It is assumed the operator is familiar with Red Hat OpenStack Platform Director (OSPD) updates, VSP installation, the distribution-specific installation and update practices, and the specific requirements for operations in a production environment.


Upgrade Paths
-------------

In this release, you can upgrade VRS and SR-IOV only from OSP Director 13 (Z12) + 5.4.1 U17 to OSP Director 13 (Z16) + 6.0.17.

These upgrade paths are not described in this document:

    * Upgrade from OpenStack releases before Queens 5.4.1 U17
    * Upgrade from VSP releases before Release 5.4.1 U17


Basic Configuration
-------------------

The basic configuration includes:

   * One or more Controller nodes
   * One or more Compute nodes (hypervisors) running the VRS and/or SR-IOV nodes running OSP Director 13 (Z12) + 5.4.1 U17


Before the Upgrade
--------------------

1. Create a single repository containing 6.0.17 Nuage packages. The repository contents may change depending on the roles configured for your deployment.

    ::

       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Group          | Packages                                     | Location (tar.gz or link)                                                                 |
       +================+==============================================+===========================================================================================+
       |                | nuage-bgp                                    | nuage-vrs-el7 or nuage-avrs-el7                                                           |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Nuage          | nuage-openstack-neutronclient                | nuage-openstack                                                                           |
       | Common         +----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Packages       | nuage-puppet-modules-6.3.0                   | https://github.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/nuage-puppet-modules       |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | nuage-metadata-agent                         | nuage-vrs-el7 or nuage-avrs-el7                                                           |
       |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | python-openswitch-nuage                      | nuage-vrs-el7 or nuage-avrs-el7                                                           |
       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Nuage VRS      | nuage-openvswitch                            | nuage-vrs-el7                                                                             |
       | Packages       +----------------------------------------------+-------------------------------------------------------------------------------------------+
       |                | selinux-policy-nuage                         | nuage-selinux                                                                             |
       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
       | Nuage SR-IOV   | nuage-topology-collector (for Nuage SR-IOV)  | nuage-openstack                                                                           |
       | packages       |                                              |                                                                                           |
       |                |                                              |                                                                                           |
       +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+


2. Make sure the Nuage 6.0.17 repository and Red Hat repositories for OSPD 13 Z16 are enabled on all Overcloud nodes.

3. Run ``yum clean all`` to clean the old yum cache on all your Overcloud modes after enabling the above yum repositories.


Update Workflow
---------------

1. Update container image source and Undercloud to OSP Director 13 Z16 by following Chapters 1, 2 and 3 from https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/index

.. Note:: Refer to the releaes notes for more information on the container images and packages on the Undercloud that are qualified in Nuage testing.


2. Back up the configuration files for your deployment.

     In the following example, all the templates and environment files for your deployment are in the /home/stack/nuage-ospdirector directory. Before getting the new Nuage 6.0.17 nuage-ospdirector/nuage-tripleoheat-templates, back up the existing files and then replace them with the new 6.0.17 codebase.

    a. Back up the templates and environment files from /home/stack/nuage-ospdirector to /home/stack/nuage-ospdirector-bk.

       ::

           $ mv /home/stack/nuage-ospdirector /home/stack/nuage-ospdirector-bk


    b. Get the tar files for the update one of these ways:

       * Download them from https://github.com/nuagenetworks/nuage-ospdirector/releases
       * Use ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b <release>``. For example, enter ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b 13.6017.1``.


    c. Copy the nuage-tripleo-heat-templates folder from /home/stack/nuage-ospdirector-osp-13.<release>/nuage-tripleo-heat-templates to /home/stack/ directory on undercloud.

        ::

            $ cd /home/stack
            $ ln -s nuage-ospdirector/nuage-tripleo-heat-templates .


3. Regenerate the roles data file by following below instructions

    a. Copy the roles from /usr/share/openstack-tripleo-heat-templates/roles to /home/stack/nuage-tripleo-heat-templates/roles

        ::

            $ cp /usr/share/openstack-tripleo-heat-templates/roles/* /home/stack/nuage-tripleo-heat-templates/roles/

    b. Run create_all_roles.sh to generate Nuage Compute roles

        ::

            $ cd /home/stack/nuage-tripleo-heat-templates/scripts/create_roles/
            $ ./create_all_roles.sh

    c. Create a *nuage_roles_data.yaml* file with all the required roles for the current Overcloud deployment.
       This example shows how to create *nuage_roles_data.yaml* with a Controller and Compute nodes for VRS and SR-IOV. The respective roles are specified in the same order. The following example has the respective role names mentioned in the same order.

        ::

            Syntax:
            openstack overcloud roles generate --roles-path /home/stack/nuage-tripleo-heat-templates/roles -o /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml Controller Compute <role> <role> ...

            Example:
            openstack overcloud roles generate --roles-path /home/stack/nuage-tripleo-heat-templates/roles -o /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml Controller Compute ComputeSriov


        .. Note:: It is not mandatory to create nuage_roles_data.yaml with all the roles shown in the example. You can specify only the required ones for your deployment.


4. Make sure your all of the templates and environment files are updated with the environment values for your deployment.

    a. Get the environment values from the /home/stack/nuage-ospdirector-bk directory and update all the templates and environment files for the deployment, such as neutron-nuage/nova-nuage.

    b. Make sure the resource_registry section of neutron-nuage-config.yaml contains the following line, which are required for 6.0.17:

        ::

            OS::TripleO::Services::NeutronCorePlugin: ../docker/services/neutron-plugin-ml2-nuage.yaml

    c. Make sure `parameter_defaults` section in  neutron-nuage-config.yaml contains following configurations, which are required for 6.0.17:

        ::

              NeutronPluginExtensions: 'nuage_network,nuage_subnet,nuage_port,port_security'
              ControllerExtraConfig:
                neutron::config::server_config:
                  DEFAULT/ipam_driver:
                    value: nuage_internal
                  DEFAULT/enable_snat_by_default:
                    value: false
                neutron::config::plugin_nuage_config:
                  PLUGIN/enable_ingress_replication:
                    value: false

    d. Make sure the resource_registry section of nova-nuage-config.yaml contains the following line, which are required for 6.0.17:

        ::

            OS::TripleO::Services::ComputeNeutronCorePlugin: ../puppet/services/nuage-compute-vrs.yaml

    e. Make sure the same network templates that were used for initial deployment are being used for update.


5. Get the latest Nuage docker images from the Red Hat Partner Registry by following these instructions in Phase 3.2. Nuage Docker Containers from `6.0/README.rst <../../README.rst>`_


6. To update the Overcloud deployment, follow these instructions: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/assembly-updating_the_overcloud


7. Once the overcloud update is complete, enable the Nuage 6.0.17 repository on the Undercloud and update nuage-topology-collector using:

    ::

        $ sudo yum update nuage-topology-collector -y


8. Run the image patching on Z17 (rhel-7.9) overcloud-full image using the latest Nuage packages to update the Overcloud images in glance. Follow the instructions in Phase 4.3: Modify the Overcloud Image from `6.0/README.rst <../../README.rst>`_