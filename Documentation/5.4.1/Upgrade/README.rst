.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

===================================
Minor Upgrade to Release 5.4.1 U12
===================================

.. contents::
   :local:
   :depth: 3


Use this documentation when upgrading between Nuage minor releases. The process applies to upgrades from Release 5.4.1U6 with RH OSPD13z7 with RHEL 7.6 or later to Release 5.4.1U12 with RH OSPD13z12 with RHEL 7.8.

During this process:

1. Nuage components are updated to 5.4.1.U12
2. Red Hat OpenStack is updated to OSPD13z12.
3. Red Hat Enterprise Linux is updated to 7.8

Note: Nuage 5.4.1.U12 release is supported with RHEL 7.8. Make sure the Red Hat Openstack Platform Director packages are updated to the z12 stream during the minor Nuage update process.


It is assumed the operator is familiar with Red Hat OpenStack Platform Director upgrades, VSP installation, the distribution-specific installation and upgrade practices, and the specific requirements for operations in a production environment.


Upgrade Paths
-------------

In this release, you can upgrade only from Queens 5.4.1 U6(RH OSPD13z7) to Queens 5.4.1 U12(RH OSPD13z12).


These upgrade paths are not described in this document:

    * Upgrade from OpenStack releases before Queens 5.4.1 U6
    * Upgrade from VSP releases before Release 5.4.1 U6


If you are upgrading from a release earlier than Queens 5.4.1 U6, refer to the Nuage Queens upgrade documentation.


Basic Configuration
---------------------

The basic configuration includes:

   * An existing installed VSD and VSC upgraded to latest VSP release
   * A single OpenStack Controller node
   * One or more Compute nodes (hypervisors) running the VRS, SR-IOV, or AVRS nodes running RHEL7.6 with OSPD13 Z7 and Nuage Release 5.4.1 U6 or later



Before the Upgrade
--------------------

1. If you are upgrading an AVRS node, migrate all your VMs on the node to an AVRS Compute node that is not being upgraded. Perform the steps in the "Live Migrate a Virtual Machine" section in https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/migrating-virtual-machines-between-compute-nodes-osp#live-migrate-a-vm-osp

2. Create the following repositories containing 5.4.1U12 nuage packages:


    * Nuage_base_repo:
  
        - It contains Selinux-policy-nuage, nuage-bgp, Python-openvswitch-nuage, nuage-openstack-neutronclient, and nuage-puppet-modules.
        - Enable this repository on the OpenStack Controller nodes, the Compute VRS nodes, and the Nova Compute AVRS nodes.
 
    * Nuage_vrs_repo:
  
        - It contains nuage-metadata-agent and nuage-openvswitch.
        - Enable this repository on the OpenStack Controller node, the Nova Compute VRS nodes and the Nova Compute Sriov nodes.
 
    * Nuage_avrs_repo:
  
        - It contains nuage-metadata-agent, nuage-openvswitch (avrs), nuage-selinux-avrs, and 6WIND packages.
        - Enable this repository on the Nova Compute AVRS nodes.

3. Make sure the Nuage 5.4.1.U12 repository and Red Hat repositories for OSPD 13 Z12 are enabled on all Overcloud nodes.

4. Please run "yum clean all" to clean the old yum cache on all your overcloud nodes after enabling above yum repositories.


Upgrade Workflow
------------------

1. Update container image source and Undercloud to OSP Director 13 Z12 by following Chapters 1, 2 and 3 from https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/index

.. Note:: Refer to the releaes notes for more information on the container images and packages on the Undercloud that are qualified in Nuage testing.


2. Back up the configuration files for your deployment.
 
     In the following example, all the templates and environment files for your deployment are in the /home/stack/nuage-ospdirector directory. Before getting the new Nuage 5.4.1 U12 nuage-ospdirector/nuage-tripleoheat-templates, back up the existing files and then replace them with the new 5.4.1 U12 codebase.
 
    a. Back up the templates and environment files from /home/stack/nuage-ospdirector to /home/stack/nuage-ospdirector-bk.
 
       ::
 
           $ mv /home/stack/nuage-ospdirector /home/stack/nuage-ospdirector-bk

 
    b. Get the tar files for the upgrade one of these ways:
 
       * Download them from https://github.com/nuagenetworks/nuage-ospdirector/releases
       * Use ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b <release>``. For example, enter ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b osp-13.541U9.1``.


    c. Copy the nuage-tripleo-heat-templates folder from /home/stack/nuage-ospdirector-osp-13.<release>/nuage-tripleo-heat-templates to /home/stack/ directory on undercloud.

        ::

            $ cd /home/stack
            $ ln -s nuage-ospdirector/nuage-tripleo-heat-templates .


3. Regenerate the roles data file by following below instructions

    a. Copy the roles from /usr/share/openstack-tripleo-heat-templates/roles to /home/stack/nuage-tripleo-heat-templates/roles

        ::

            $ cp /usr/share/openstack-tripleo-heat-templates/roles/* /home/stack/nuage-tripleo-heat-templates/roles/

    b. Run create_compute_avrs_role.sh to generate updated ComputeAvrs role

        ::

            $ cd home/stack/nuage-tripleo-heat-templates/scripts/create_roles/
            $ ./create_compute_avrs_role.sh

    c. Generate roles data file to use updated ComputeAvrs role

        ::

            $ openstack overcloud roles generate --roles-path /home/stack/nuage-tripleo-heat-templates/roles/ -o /home/stack/nuage-tripleo-heat-templates/templates/<roles_data file name> Controller Compute ComputeAvrs


3. Make sure your all of the templates and environment files are updated with the environment values for your deployment.

    a. Get the environment values from the /home/stack/nuage-ospdirector-bk directory and update all the templates and environment files for the deployment, such as neutron-nuage/nova-nuage/compute-avrs.
 
    b. Make sure the resource_registry section of neutron-nuage-config.yaml contains the following line, which was added in Release 5.4.1 U12:
 
        ::

            OS::TripleO::Services::NeutronCorePlugin: ../docker/services/neutron-plugin-ml2-nuage.yaml

    c. Make sure the resource_registry section of nova-nuage-config.yaml contains the following line, which was added in Release 5.4.1 U12:

        ::

            OS::TripleO::Services::ComputeNeutronCorePlugin: ../puppet/services/nuage-compute-vrs.yaml

    d. For Avrs deployments, make sure the resource_registry section of compute-avrs-environment.yaml contains the following line, which was added in Release 5.4.1 U12:

        ::

            OS::TripleO::Services::NovaComputeAvrs: ../docker/services/nova-compute-avrs.yaml
            OS::TripleO::Services::ComputeNeutronCorePluginNuage: ../puppet/services/neutron-compute-plugin-nuage.yaml


4. Get the latest Nuage docker images from the Red Hat Partner Registry by following these instructions in Phase 8. Nuage Docker Containers from `5.4.1/README.rst <../../README.rst>`_


5. To update the Overcloud deployment, follow these instructions: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/assembly-updating_the_overcloud


6. To complete the overcloud upgrade, a reboot is needed to load the updated kernel. For this procedure we refer to the official documentation https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/rebooting-the-overcloud


7. Run the image patching on Z12 (rhel-7.8) overcloud-full image using the latest Nuage packages to update the Overcloud image. Follow these instructions: `README.md <../../../image-patching/README_5.0.md>`_


Post Upgrade Verifications
--------------------------

  - The controllers and the computes should have RHOSP release 13z12

        ::

            [heat-admin@overcloud-computeavrs-1 ~]$ cat /etc/rhosp-release
            Red Hat OpenStack Platform release 13.0.12 (Queens)


  - The controllers and the computes should have RHEL 7.8

        ::

            [heat-admin@overcloud-computeavrs-1 ~]$ cat /etc/redhat-release
            Red Hat Enterprise Linux Server release 7.8 (Maipo)


  - The controllers and the computes should have the RHEL 7.8 kernel

        ::

            [heat-admin@overcloud-computeavrs-1 ~]$ uname -a
            Linux overcloud-computeavrs-1 3.10.0-1127.13.1.el7.x86_64 #1 SMP Fri Jun 12 14:34:17 EDT 2020 x86_64 x86_64 x86_64 GNU/Linux


  - The computes should have the 5.4.1.U12 nuage-openvswitch version.

        ::

            [heat-admin@overcloud-compute-1 ~]$ sudo ovs-appctl version
            ovs-vswitchd (Open vSwitch) 5.4.1-443-nuage
            Compiled Jul  9 2020 22:38:51
            Open vSwitch base release: 0x250

            [heat-admin@overcloud-computeavrs-1 ~]$ sudo ovs-appctl version
            ovs-vswitchd (Open vSwitch) 5.4.1-443-6wind-nuage
            Compiled Jul  9 2020 23:00:28
            Open vSwitch base release: 0x250


  - The computes should have the 5.4.1.U12 nuage rmps

        ::

            [heat-admin@overcloud-compute-1 ~]$ rpm -qa | grep nuage
            nuage-openstack-neutronclient-6.5.0-5.4.1_336_nuage.noarch
            nuage-bgp-5.4.1-443.x86_64
            python-openvswitch-nuage-5.4.1-443.6wind.el7.x86_64
            selinux-policy-nuage-5.4.1-443.el7.x86_64
            nuage-openvswitch-5.4.1-443.el7.x86_64
            nuage-puppet-modules-5.4-0.x86_64
            nuage-metadata-agent-5.4.1-443.el7.x86_64

            [heat-admin@overcloud-computeavrs-1 ~]$ rpm -qa | grep "nuage\|6wind\|virtual"
            6windgate-linux-fp-sync-vrf-4.23.12.NUAGE.5-0.x86_64
            6windgate-tools-common-libs-pyroute2-0.4.13-6windgate.4.23.12.NUAGE.5.x86_64
            nuage-openvswitch-5.4.1-443.6wind.el7.x86_64
            6windgate-linux-fp-sync-4.23.12.NUAGE.5-0.x86_64
            nuage-openstack-neutronclient-6.5.0-5.4.1_336_nuage.noarch
            nuage-bgp-5.4.1-443.x86_64
            python-pyelftools-0.24-6windgate.4.23.12.NUAGE.5.x86_64
            6windgate-dpdk-pmd-mellanox-rdma-core-4.23.12.NUAGE.5-0.x86_64
            6windgate-tools-common-libs-daemonctl-4.23.12.NUAGE.5-0.x86_64
            6windgate-fp-ovs-4.23.12.NUAGE.5-0.x86_64
            6windgate-dpdk-pmd-virtio-host-4.23.12.NUAGE.5-0.x86_64
            virtual-accelerator-base-1.9.12.NUAGE.5-0.x86_64
            python-openvswitch-nuage-5.4.1-443.6wind.el7.x86_64
            selinux-policy-nuage-5.4.1-443.el7.x86_64
            6windgate-fpn-sdk-dpdk-4.23.12.NUAGE.5-0.x86_64
            6windgate-fp-4.23.12.NUAGE.5-0.x86_64
            6windgate-linux-fp-sync-fptun-4.23.12.NUAGE.5-0.x86_64
            nuage-metadata-agent-5.4.1-443.6wind.el7.x86_64
            nuage-puppet-modules-5.4-0.x86_64
            6windgate-dpdk-4.23.12.NUAGE.5-0.x86_64
            6windgate-linux-fp-sync-ovs-4.23.12.NUAGE.5-0.x86_64
            selinux-policy-nuage-avrs-5.4.1-443.el7.x86_64
            6windgate-tools-common-libs-libconsole-4.23.12.NUAGE.5-0.x86_64
            6windgate-product-base-4.23.12.NUAGE.5-0.x86_64


  - The computes should now have the Nuage VXLAN iptables rule as stateless

        ::

            [heat-admin@overcloud-compute-1 ~]$ sudo iptables -L | grep udp | grep '118 neutron stateless vxlan networks ipv4'
            ACCEPT     udp  --  anywhere             anywhere             multiport dports 4789 /* 118 neutron stateless vxlan networks ipv4 */


  - The controllers should have the 5.4.1.U12 nuage and RHEL 7.8 RHOSP container images

        ::

            [heat-admin@overcloud-controller-0  ~]$ sudo docker ps | grep nuagenetworks
            CONTAINER ID        IMAGE                                                                                COMMAND                  CREATED             STATUS                       PORTS               NAMES
            5551a936e20c        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-api-cfn-5-4-1-u12:13.0-1     "dumb-init --singl..."   About an hour ago   Up About an hour (healthy)                       heat_api_cfn
            5b44b601ba32        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-neutron-server-5-4-1-u12:13.0-1   "dumb-init --singl..."   About an hour ago   Up About an hour (healthy)                       neutron_api
            a383e8dbd9d6        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-api-5-4-1-u12:13.0-1         "dumb-init --singl..."   About an hour ago   Up About an hour                                 heat_api_cron
            13458926249e        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-engine-5-4-1-u12:13.0-1      "dumb-init --singl..."   About an hour ago   Up About an hour (healthy)                       heat_engine
            2e6a15ec4835        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-api-5-4-1-u12:13.0-1         "dumb-init --singl..."   About an hour ago   Up About an hour (healthy)                       heat_api
            60b847ffc718        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-horizon-5-4-1-u12:13.0-1          "dumb-init --singl..."   About an hour ago   Up About an hour                                 horizon


- The kmods are properly build for AVRS computes

        ::

            [heat-admin@overcloud-computeavrs-1 ~]$ dkms status
            fpn-sdk, 4.23.12.NUAGE.5, 3.10.0-1127.13.1.el7.x86_64, x86_64: installed
            fpn-sdk, 4.23.12.NUAGE.5, 3.10.0-957.21.3.el7.x86_64, x86_64: installed
            fptun, 4.23.12.NUAGE.5, 3.10.0-1127.13.1.el7.x86_64, x86_64: installed
            fptun, 4.23.12.NUAGE.5, 3.10.0-957.21.3.el7.x86_64, x86_64: installed
            vrf, 4.23.12.NUAGE.5, 3.10.0-1127.13.1.el7.x86_64, x86_64: installed
            vrf, 4.23.12.NUAGE.5, 3.10.0-957.21.3.el7.x86_64, x86_64: installed
