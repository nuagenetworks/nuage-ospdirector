.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

===================================
Minor Update to Release 6.0.19
===================================

.. contents::
   :local:
   :depth: 3


Use this documentation when updating between nuage minor releases. The process applies to updates from Release 6.0.10 (RHEL 7.8 with RHOSP13z12) to Release 6.0.19 (RHEL 7.9 with RHOSP13z16).

It is assumed the operator is familiar with Red Hat OpenStack Platform Director updates, VSP installation, the distribution-specific installation and update practices, and the specific requirements for operations in a production environment.

Note: Nuage 6.0.19 release is supported with RHEL 7.9 with RHOSP13z16.


Update Paths
-------------

In this release, you can update only from OSP Director 13 (z12) + 6.0.10 to OSP Director 13 (z16) + 6.0.19.


These update paths are not described in this document:

    * Update from OpenStack releases before Queens 6.0.10


Basic Configuration
---------------------

The basic configuration includes:

   * One or more Controller node(s) running Release 6.0.10 (RHEL 7.8 with RHOSP13z12)
   * One or more Compute nodes (hypervisors) running the HW-VTEP nodes running Release 6.0.10 (RHEL 7.8 with RHOSP13z12)


Before the Upgrade
--------------------

1. Make sure the Red Hat repositories for OSPD 13 RHOSP13z16 and RHEL 7.9 are enabled on all Overcloud nodes.

2. Please run "yum clean all" to clean the old yum cache on all your overcloud nodes after enabling above yum repositories.


Update Workflow
---------------

1. Update container image source and Undercloud to OSP Director 13 z16 by following Chapters 1, 2 and 3 from https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/index

.. Note:: Refer to the release notes for more information on the container images and packages on the Undercloud that are qualified in Nuage testing.


2. Back up the configuration files for your deployment.

     In the following example, all the templates and environment files for your deployment are in the /home/stack/nuage-ospdirector directory. To get new the Nuage 6.0.19 nuage-ospdirector/nuage-tripleo-heat-templates, back up the files before replacing the existing ones with new 6.0.19 codebase.

    a. Back up the templates and environment files from /home/stack/nuage-ospdirector to /home/stack/nuage-ospdirector-bk.

       ::

           $ mv /home/stack/nuage-ospdirector /home/stack/nuage-ospdirector-bk


    b. Get the tar files for the update one of these ways:

       * Download them from https://github.com/nuagenetworks/nuage-ospdirector/releases
       * Use ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b <release>``. For example, enter ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b 13.6019.1``.


    c. Copy the nuage-tripleo-heat-templates folder from /home/stack/nuage-ospdirector-osp-13.<release>/nuage-tripleo-heat-templates to /home/stack/ directory on undercloud.

        ::

            $ cd /home/stack
            $ ln -s nuage-ospdirector/nuage-tripleo-heat-templates .


3. Regenerate roles data file by following below instructions

    a. Create a nuage_roles_data.yaml file with all the required roles for the current Overcloud deployment.

       This example shows how to create nuage_roles_data.yaml with a Controller, Compute, ComputeSriov and ComputeOvsDpdk roles.

        ::

            openstack overcloud roles generate -o /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml Controller Compute ComputeSriov ComputeOvsDpdk


    b. Create node-info.yaml in /home/stack/templates/ and specify the roles and number of nodes

        ::

            Syntax:
            parameter_defaults:
              Overcloud<Role Name>Flavor: <flavor name>
              <Role Name>Count: <number of nodes for this role>


            Example:

            parameter_defaults:
              OvercloudControllerFlavor: control
              ControllerCount: 3
              OvercloudComputeFlavor: compute
              ComputeCount: 2


4. Get the environment values from the /home/stack/nuage-ospdirector-bk directory and update all the templates and environment files for the deployment, such as neutron-nuage/nova-nuage.


5. Get the latest Nuage docker images from the Red Hat Partner Registry by following these instructions in Phase 3.2. Nuage Docker Containers from `6.0_HWVTEP/README.rst <../../README.rst>`_


6. To update the Overcloud deployment, follow these instructions: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/assembly-updating_the_overcloud


    a. An Overcloud Upgrade has 3 major steps:

        ::

            openstack overcloud update prepare
            openstack overcloud update run --nodes <role-name>
            openstack overcloud update converge


    b. Update overcloud qcow for future scale-outs.

7. If neutron DHCP is deployed in the setup, re-run the topology collector.

        ::

            python2.7 /opt/nuage/topology-collector/nuage_topology_collector/scripts/generate_topology.py


Post Upgrade Verification
-------------------------

1. Make sure the Controller node(s) are running with RHEL 7.9 + Nuage 6.0.19 container images.


    ::
        [heat-admin@ci-hwvtep-dpdk-up-3261-controller-0 ~]$ cat /etc/redhat-release
        Red Hat Enterprise Linux Server release 7.9 (Maipo)
        [heat-admin@ci-hwvtep-dpdk-up-3261-controller-0 ~]$ sudo docker ps | grep nuage
        db318c0aaaff        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-api-cfn-6-0-19:latest        "dumb-init --singl..."   34 minutes ago      Up 34 minutes (healthy)                       heat_api_cfn
        0d9c80d69722        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-neutron-server-6-0-19:latest      "dumb-init --singl..."   34 minutes ago      Up 34 minutes (healthy)                       neutron_api
        2cebd7c1329b        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-api-6-0-19:latest            "dumb-init --singl..."   34 minutes ago      Up 34 minutes                                 heat_api_cron
        cc128430d521        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-engine-6-0-19:latest         "dumb-init --singl..."   34 minutes ago      Up 34 minutes (healthy)                       heat_engine
        29e5c9f3bac5        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-api-6-0-19:latest            "dumb-init --singl..."   35 minutes ago      Up 35 minutes (healthy)                       heat_api
        a372ed2e6914        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-horizon-6-0-19:latest             "dumb-init --singl..."   38 minutes ago      Up 38 minutes                                 horizon


2. Make sure the Compute nodes (hypervisors) running with RHEL 7.9.

    ::
        [heat-admin@ci-hwvtep-dpdk-up-3261-computesriov-0 ~]$ cat /etc/redhat-release
        Red Hat Enterprise Linux Server release 7.9 (Maipo)
