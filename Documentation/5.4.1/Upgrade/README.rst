.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

===================================
Minor Upgrade to Release 5.4.1 U16
===================================

.. contents::
   :local:
   :depth: 3


Use this documentation when upgrading between Nuage minor releases. The process applies to upgrades from Release 5.4.1U12 with RH OSPD13z12 with RHEL 7.8 or later to Release 5.4.1U16 with RH OSPD13z12 with RHEL 7.8.

During this process:

1. Nuage components are updated to 5.4.1.U16
2. Red Hat OpenStack stays as OSPD13z12.
3. Red Hat Enterprise Linux stays as 7.8

Note: Nuage 5.4.1.U16 release is supported with RHEL 7.8. Make sure the Red Hat Openstack Platform Director packages are updated to the z12 stream during the minor Nuage update process.


It is assumed the operator is familiar with Red Hat OpenStack Platform Director upgrades, VSP installation, the distribution-specific installation and upgrade practices, and the specific requirements for operations in a production environment.


Upgrade Paths
-------------

In this release, you can upgrade only from Queens 5.4.1 U12(RH OSPD13z12) to Queens 5.4.1 U16(RH OSPD13z12).


These upgrade paths are not described in this document:

    * Upgrade from OpenStack releases before Queens 5.4.1 U12
    * Upgrade from VSP releases before Release 5.4.1 U12


If you are upgrading from a release earlier than Queens 5.4.1 U12, refer to the Nuage Queens upgrade documentation.


Basic Configuration
---------------------

The basic configuration includes:

   * An existing installed VSD and VSC upgraded to latest VSP release
   * A single OpenStack Controller node
   * One or more Compute nodes (hypervisors) running the VRS, SR-IOV, or AVRS nodes running RHEL7.8 with OSPD13 Z12 and Nuage Release 5.4.1 U12 or later



Before the Upgrade
--------------------

1. Create the following repositories containing 5.4.1U16 nuage packages:


    * Nuage_base_repo:

        - It contains Selinux-policy-nuage, nuage-bgp, Python-openvswitch-nuage, nuage-openstack-neutronclient, and nuage-puppet-modules.
        - Enable this repository on the OpenStack Controller nodes, the Compute VRS nodes, and the Nova Compute AVRS nodes.

    * Nuage_vrs_repo:

        - It contains nuage-metadata-agent and nuage-openvswitch.
        - Enable this repository on the OpenStack Controller node, the Nova Compute VRS nodes and the Nova Compute Sriov nodes.

    * Nuage_avrs_repo:

        - It contains nuage-metadata-agent, nuage-openvswitch (avrs), nuage-selinux-avrs, and 6WIND packages.
        - Enable this repository on the Nova Compute AVRS nodes.

2. Make sure the Nuage 5.4.1.U16 repository and Red Hat repositories for OSPD 13 Z12 are enabled on all Overcloud nodes.

3. Please run "yum clean all" to clean the old yum cache on all your overcloud nodes after enabling above yum repositories.


Upgrade Workflow
------------------

1. Update container image source and Undercloud to OSP Director 13 Z12 by following Chapters 1, 2 and 3 from https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/index

.. Note:: Refer to the releaes notes for more information on the container images and packages on the Undercloud that are qualified in Nuage testing.


2. Back up the configuration files for your deployment.

     In the following example, all the templates and environment files for your deployment are in the /home/stack/nuage-ospdirector directory. Before getting the new Nuage 5.4.1 U16 nuage-ospdirector/nuage-tripleoheat-templates, back up the existing files and then replace them with the new 5.4.1 U16 codebase.

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


4. Get the latest Nuage docker images from the Red Hat Partner Registry by following these instructions in Phase 8. Nuage Docker Containers from `5.4.1/README.rst <../../README.rst>`_


5. To update the Overcloud deployment, follow these instructions: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/assembly-updating_the_overcloud.

    a. An Overcloud Upgrade has 3 major steps

        * openstack overcloud update prepare
        * openstack overcloud update run --nodes <role-name>
        * openstack overcloud update converge

    b. In order to use HW CPP functionality on AVRS computes, update the FastPathNIc configuration before doing the 'update converge.

       Once 'openstack overcloud update run' finished, before running 'openstack overcloud update converge', update the compute-avrs-environment.yaml template, e.g. add :

        ::

            FastPathNicDescriptors: "--rx-cp-filter-mode=dedicated-queue --tx-cp-filter-mode=software-filter --cp-filter-virtual-ports=enable --cp-filter-cpu-budget=10 --nb-rxd=4096 --nb-txd=4096 --rx-cp-filter-threshold=75% --tx-cp-filter-threshold=75%"


       For more information and details about the HW CPP feature and parameters please refer to the VSP documentation.

6. Run the image patching on Z12 (rhel-7.8) overcloud-full image using the latest Nuage packages to update the Overcloud image. Follow these instructions: `README.md <../../../image-patching/README_5.0.md>`_


Post Upgrade Verifications
--------------------------

  - The computes should have the 5.4.1.U12 nuage-openvswitch version.

        ::

            [heat-admin@overcloud-compute-1 ~]$ sudo ovs-appctl version
            ovs-vswitchd (Open vSwitch) 5.4.1-523-nuage
            Compiled Jul  9 2020 22:38:51
            Open vSwitch base release: 0x250

            [heat-admin@overcloud-computeavrs-1 ~]$ sudo ovs-appctl version
            ovs-vswitchd (Open vSwitch) 5.4.1-523-6wind-nuage
            Compiled Jul  9 2020 23:00:28
            Open vSwitch base release: 0x250


  - The computes should have the 5.4.1.U16 nuage rmps

        ::

            [heat-admin@overcloud-compute-1 ~]$ rpm -qa | grep nuage
            nuage-metadata-agent-5.4.1-523.el7.x86_64
            selinux-policy-nuage-5.4.1-443.el7.x86_64
            nuage-bgp-5.4.1-483.x86_64
            nuage-openstack-neutronclient-6.5.0-5.4.1_524_nuage.noarch
            nuage-openvswitch-5.4.1-523.el7.x86_64
            nuage-puppet-modules-5.4-0.x86_64
            python-openvswitch-nuage-5.4.1-523.el7.x86_64

            [heat-admin@overcloud-computeavrs-1 ~]$ rpm -qa | grep "nuage\|6wind\|virtual"
            6windgate-linux-fp-sync-4.23.12.NUAGE.13-0.x86_64
            nuage-bgp-5.4.1-483.x86_64
            6windgate-dpdk-pmd-virtio-host-4.23.12.NUAGE.13-0.x86_64
            6windgate-linux-fp-sync-fptun-4.23.12.NUAGE.13-0.x86_64
            6windgate-fpn-sdk-dpdk-4.23.12.NUAGE.13-0.x86_64
            nuage-openvswitch-5.4.1-523.6wind.el7.x86_64
            selinux-policy-nuage-5.4.1-443.el7.x86_64
            6windgate-tools-common-libs-daemonctl-4.23.12.NUAGE.13-0.x86_64
            6windgate-tools-common-libs-pyroute2-0.4.13-6windgate.4.23.12.NUAGE.13.x86_64
            nuage-metadata-agent-5.4.1-523.6wind.el7.x86_64
            6windgate-linux-fp-sync-vrf-4.23.12.NUAGE.13-0.x86_64
            6windgate-product-base-4.23.12.NUAGE.13-0.x86_64
            virtual-accelerator-base-1.9.12.NUAGE.13-0.x86_64
            6windgate-dpdk-pmd-mellanox-rdma-core-4.23.12.NUAGE.13-0.x86_64
            6windgate-fp-ovs-4.23.12.NUAGE.13-0.x86_64
            nuage-openstack-neutronclient-6.5.0-5.4.1_524_nuage.noarch
            6windgate-tools-common-libs-libconsole-4.23.12.NUAGE.13-0.x86_64
            6windgate-fp-4.23.12.NUAGE.13-0.x86_64
            selinux-policy-nuage-avrs-5.4.1-443.el7.x86_64
            python-openvswitch-nuage-5.4.1-523.6wind.el7.x86_64
            6windgate-dpdk-4.23.12.NUAGE.13-0.x86_64
            6windgate-linux-fp-sync-ovs-4.23.12.NUAGE.13-0.x86_64
            nuage-puppet-modules-5.4-0.x86_64


  - The computes should now have the Nuage VXLAN iptables rule as stateless

        ::

            [heat-admin@overcloud-compute-1 ~]$ sudo iptables -L | grep udp | grep '118 neutron stateless vxlan networks ipv4'
            ACCEPT     udp  --  anywhere             anywhere             multiport dports 4789 /* 118 neutron stateless vxlan networks ipv4 */


  - The controllers should have the 5.4.1.U16 nuage and RHEL 7.8 RHOSP container images

        ::

            [heat-admin@overcloud-controller-0  ~]$ sudo docker ps | grep nuagenetworks
            CONTAINER ID        IMAGE                                                                                COMMAND                  CREATED             STATUS                       PORTS               NAMES
            7934af1bd9bf        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-neutron-server-5-4-1-u16:latest   "dumb-init --singl..."   About an hour ago   Up About an hour (healthy)                       neutron_api
            720c3881257f        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-api-5-4-1-u16:latest         "dumb-init --singl..."   About an hour ago   Up About an hour                                 heat_api_cron
            2bac3ff0d02f        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-api-cfn-5-4-1-u16:latest     "dumb-init --singl..."   About an hour ago   Up About an hour (healthy)                       heat_api_cfn
            32d15910de69        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-engine-5-4-1-u16:latest      "dumb-init --singl..."   About an hour ago   Up About an hour (healthy)                       heat_engine
            a345d417faa0        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-heat-api-5-4-1-u16:latest         "dumb-init --singl..."   About an hour ago   Up About an hour (healthy)                       heat_api
            2b3529c1ab4d        192.168.200.1:8787/nuagenetworks/rhosp13-openstack-horizon-5-4-1-u16:latest          "dumb-init --singl..."   About an hour ago   Up About an hour                                 horizon


- The kmods are properly build for AVRS computes

        ::

            [heat-admin@overcloud-computeavrs-1 ~]$ dkms status
            fpn-sdk, 4.23.12.NUAGE.13, 3.10.0-1127.19.1.el7.x86_64, x86_64: installed
            fptun, 4.23.12.NUAGE.13, 3.10.0-1127.19.1.el7.x86_64, x86_64: installed
            vrf, 4.23.12.NUAGE.13, 3.10.0-1127.19.1.el7.x86_64, x86_64: installed
