.. _queens-80-ospd:

.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

.. NOTES do not render correctly in the GitHub Preview, BUT they do in the HTML output, so do not worry!


.. .. Date, Version and Author
.. .. ==========================
.. ..
.. ..  =========  =======    =========
.. ..  Date       Version    Author
.. ..  =========  =======    =========
.. ..  05/24/18    5.3.2     Jennifer - Create new document for Queens ML2 based on the 5.3.1 Queens files.
.. ..  08/02/18    5.3.2     Jennifer - Installation procedure for Queens is to use OSPD 13. Wiki is here: https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/wiki/Nuage-OSP-Director-13-Integration
.. ..  09/05/18 to
.. ..  09/10/18    5.3.2 U2   Jennifer - Add the SR-IOV Installation procedure for Queens. Wiki is here: https://github.mv.usa.alcatel.com/speesapa/Nuage-Queens-OSPD/wiki/Sriov in PR 3078, PR 3087, and PR 3090
.. ..  09/11/18    5.3.2 U2   Add link for the ospd sriov documentation to what needs to be done next after the deployment;  also mention that we expect the user to actually install and run the topology collector manually to setup the controller and reference sriov documentation on how to run it.
.. ..  09/12/18    5.3.3     Jennifer - Add 5.3.2 U2 updates to the master branch.
.. ..  10/23/18    5.3.3     Jennifer - DOC-2112
.. ..  10/24/18    5.3.3     Jennifer - DOC-2105 - AVRS


======================================================
Deploying Queens Using OpenStack Platform Director 13
======================================================

This section contains the following topics:

.. contents::
   :local:
   :depth: 3


OpenStack Platform Director
------------------------------

The Red Hat OpenStack Platform director is a toolset for installing and managing an OpenStack environment. It is based primarily on the OpenStack TripleO project. It uses an OpenStack deployment, referred to as the Undercloud, to deploy an OpenStack cluster, referred to as an Overcloud.

The OpenStack Platform director (also referred to as OpenStack director) is an image-based installer. It uses a single image (for example, overcloud-full.qcow2) that is deployed on the Controller and Compute nodes belonging to the OpenStack cluster (Overcloud). This image contains all the packages needed during the deployment. The deployment creates only the configuration files and databases required by the different services and starts the services in the correct order. During a deployment, no new software is installed.

For integration of OpenStack Platform director with the Nuage plugin, use the command-line based template option.

OpenStack director uses Heat to orchestrate the deployment of an OpenStack environment. The actual deployment is done through Heat templates and Puppet. Users provide any custom input in templates using the ``openstack overcloud deploy`` command. When this command is run, all the templates are parsed to create the Hiera database, and then a set of puppet manifests, also referred to as TripleO Heat templates, are run to complete the deployment. The Puppet code in turn uses the Puppet modules developed to deploy different services of OpenStack (such as puppet-nova, puppet-neutron, and puppet-cinder).

The OpenStack Platform director architecture allows partners to create custom templates. Partners create new templates to expose parameters specific to their modules.  These templates can then be passed through the ``openstack overcloud deploy`` command during the deployment. Changes to the Puppet manifests are required to handle the new values in the Hiera database and to act on them to deploy the partner software.


Requirements
-------------

For Overcloud, networking, Undercloud, and repository requirements, see the Red Hat upstream documentation:
https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/ .

VSP requirements:

   * VSD and VSC are set up before running OpenStack Platform director.
   * Your network includes redundant VSDs.
   * Manual Horizon and Heat integration for Nuage Extensions are required because these modules are not part of the packaged integration.


RHEL 7.5 is supported with OSP 13.

Recommended Topologies
-----------------------

We recommend deploying this topology:

   * Cluster deployment with redundant controllers


The cluster in your Layer 3 (L3) network should have the following components:


.. _infrastructure_required:

.. figure:: graphics/infrastructure_required.PNG

These networks are used:

   * The External network provides Internet access to the VMs using the br-ext mechanisms and floating IP (FIP) addresses and/or Port Address Translation (PAT). It is secured using ACLs on the VSG.
   * The Management network is used for FIP traffic and Internet access for all VMs.
   * The Public API network is used for the public API, API management by administrators, and OpenStack Platform cluster management traffic.
   * The Tenant subnet is used for VXLAN tunnels between the OpenStack Platform Compute nodes, OpenStack controller, VSC, and VSG.


The cluster requires the following:

   * A VSD node can be installed as a VM or a bare metal server.
   * For high availability of the VSD nodes, use a load balancer across the VSD nodes for the REST API.
   * The VSC is always installed as a VM.



Best Practices
---------------

Nuage VSD and VSC

    * Add an endpoint on the provisioned network for verification and testing (when connecting to isolated networks).
    * The Layer 3 network has redundant VSDs.


Red Hat

    * During the certification process, the network should have an odd number of controllers so that the majority of the nodes are up if a node goes down.
    * Go to https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/ for more Red Hat best practices.


Integrating Nuage VSP with OpenStack Platform Director
-------------------------------------------------------

The integration includes the following steps:

* Modifying the Overcloud qcow image (for example, overcloud-full.qcow2)

    - The Nuage VRS and metadata agent configuration files need to be created and populated with the required parameters. To do this, add the puppet module (nuage-puppet-modules) to the Overcloud image with the other required Nuage RPMs.

    - The typical OpenStack director deployment scenario assumes that all the packages are installed on the overcloud-full image. The Overcloud qcow image (for example, overcloud-full.qcow2) needs to be patched with the following RPMs:

        - nuage-bgp
        - nuage-metadata-agent
        - nuage-openstack-heat
        - nuage-openstack-horizon
        - nuage-openstack-neutron
        - nuage-openstack-neutronclient
        - nuage-openvswitch (Nuage VRS)
        - nuage-puppet-modules-5.0
        - selinux-policy-nuage
        - nuage-topology-collector

    - Uninstall Open vSwitch (OVS).
    - Install VRS (nuage-openvswitch).

    - Use nuage-puppet-modules-5.0.x86_64.rpm and the nuage_overcloud_full_patch.py script to patch to the Overcloud qcow image, uninstall Open vSwitch (OVS), and install VRS.

    - For AVRS integration, the overcloud-full image is also patched with following 6WIND and Nuage AVRS RPMs:

        - 6windgate-dpdk
        - 6windgate-dpdk-pmd-mellanox-ofa-kernel
        - 6windgate-dpdk-pmd-mellanox-rdma-core
        - 6windgate-dpdk-pmd-virtio-host
        - 6windgate-fp
        - 6windgate-fpn-sdk-dpdk
        - 6windgate-fp-ovs
        - 6windgate-linux-fp-sync
        - 6windgate-linux-fp-sync-fptun
        - 6windgate-linux-fp-sync-ovs
        - 6windgate-linux-fp-sync-vrf
        - 6windgate-product-base
        - 6windgate-qlogic-fastlinq
        - 6windgate-tools-common-libs-daemonctl
        - 6windgate-tools-common-libs-libconsole
        - 6windgate-tools-common-libs-pyroute2
        - 6wind-openstack-extensions
        - dkms
        - nuage-metadata-agent (6wind version)
        - nuage-openvswitch (6wind version)
        - selinux-policy-nuage-avrs
        - python-pyelftools
        - virtual-accelerator
        - virtual-accelerator-addon-mellanox
        - virtual-accelerator-base


* Updating the Undercloud codebase

    - Apply the changes in the diff files in https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/tripleo-heat-templates-diff to the Undercloud codebase.
    - The instructions to apply the patch script are in this README file: https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/tripleo-heat-templates-diff/README.md .
    - For AVRS integration, get the script and files to patch the Overcloud image with the AVRS RPMs.

* Updating the TripleO Heat templates (also referred to as the puppet manifests)

    - Some of the parameters in ``neutron.conf`` and ``nova.conf`` need to be configured in the Heat templates. The Nuage VRS and metadata agent also need to be configured. The values for these parameters depend on the Nuage VSP configuration.
      We use ``neutron-nuage-config.yaml`` and ``nova-nuage-config.yaml`` environment files to configure these values.
    - See the `Sample Templates`_ section for some probable values of the parameters in the ``neutron-nuage-config.yaml`` and ``nova-nuage-config.yaml`` files.
    - For AVRS integration, some of the parameters in ``fast-path.env`` needs to be configured in the Heat templates. We use ``avrs-environment.yaml`` environment file to configure these values.
    - For AVRS integration, see the `Sample Templates`_ section for some probable values of the parameters in the ``avrs-environment.yaml`` file and we also need to create a new AVRS role similar to the upstream Compute role.


* Updating the Docker Images

    Some Nuage Docker images are not in the Red Hat registry. Use the following required Docker files and instructions provided by Nuage:

    - nuage-openstack-neutron
    - nuage-openstack-neutronclient
    - nuage-openstack-horizon
    - nuage-openstack-heat
    - For AVRS integration only, nova-compute-avrs

Links to Nuage and OpenStack Resources
---------------------------------------

* For the Heat templates used by OpenStack director, go to http://git.openstack.org/cgit/openstack/tripleo-heat-templates .
* For the Puppet manifests, go to http://git.openstack.org/cgit/openstack/tripleo-heat-templates/tree/puppet .
* For the nuage-puppet-modules RPM (nuage-puppet-modules-5.0), go to https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/image-patching .
* For the script to patch the Overcloud qcow image (nuage_overcloud_full_patch.py), go to https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/blob/OSPD13/image-patching/stopgap-script/nuage_overcloud_full_patch.py .
* For the Nuage and Puppet modules, go to http://git.openstack.org/cgit/openstack/tripleo-heat-templates/tree/puppet .
* For the files and script to generate the CMS ID, go to https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/generate-cms-id .


Before the Deployment Process
------------------------------

.. Note:: Before performing the procedures in this document, read the *Director Installation and Usage* guide for OSPD 13: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage .

Create separate repositories for the following packages:

    * OSC and VRS: `OSC and VRS Packages`_
    * 6WIND and AVRS ( Only for AVRS Deployment) : `6WIND and AVRS Packages`_


OSC and VRS Packages
~~~~~~~~~~~~~~~~~~~~~~

    * Nuage-bgp
    * Nuage-metadata-agent
    * Nuage-nova-extensions
    * Nuage-openstack-heat
    * Nuage-openstack-horizon
    * Nuage-openstack-neutron
    * Nuage-openstack-neutronclient
    * nuage-openvswitch (VRS)
    * nuage-puppet-modules (Latest version 5.0)
    * Nuage-topology-collector
    * Selinux-policy-nuage


6WIND and AVRS Packages
~~~~~~~~~~~~~~~~~~~~~~~~~

    * 6wind-openstack-extensions
    * 6windgate-dpdk
    * 6windgate-dpdk-pmd-mellanox-ofa-kernel
    * 6windgate-dpdk-pmd-mellanox-rdma-core
    * 6windgate-dpdk-pmd-virtio-host
    * 6windgate-fp
    * 6windgate-fp-ovs
    * 6windgate-fpn-sdk-dpdk
    * 6windgate-linux-fp-sync
    * 6windgate-linux-fp-sync-fptun
    * 6windgate-linux-fp-sync-ovs.
    * 6windgate-linux-fp-sync-vrf
    * 6windgate-product-base
    * 6windgate-tools-common-libs-daemonctl
    * 6windgate-tools-common-libs-libavl
    * 6windgate-tools-common-libs-libconsole
    * 6windgate-tools-common-libs-libssh
    * 6windgate-tools-common-libs-pyroute2
    * Python-pyelftools
    * Dkms
    * Elfutils
    * Elfutils-default-yama-scope
    * Elfutils-libelf
    * Elfutils-libelf-devel
    * Elfutils-libs
    * nuage-metadata-agent (from el7-6wind)
    * nuage-openvswitch (from el7-6wind)
    * Virtual-accelerator
    * Virtual-accelerator-addon-mellanox
    * Virtual-accelerator-base
    * selinux-policy-nuage-avrs


Deployment Process
-------------------

Phase 1: Install OpenStack director on the Undercloud system.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow the steps in https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/installing-the-undercloud .

When obtaining images for the Overcloud nodes, replace the upstream Overcloud image with one modified to include Nuage components from Step 2 in this workflow.

If you want to use a remote registry for the Overcloud container images, you need to add the iptables rule on Director (Undercloud Machine) with the Undercloud IP address for NAT. In this example, the Undercloud IP address is 192.168.24.1:

::

    sudo iptables -A POSTROUTING -t nat -s 192.168.24.1/24 -j MASQUERADE


Phase 2: Modify the Overcloud qcow image (for example, overcloud-full.qcow2) to include Nuage components.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The steps for modifying overcloud-full.qcow2 are provided in the README.md file: https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/image-patching/stopgap-script/README.md .


Phase 3: Update the Undercloud codebase.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow the instructions in `README.md
<https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/tripleo-heat-templates-diff/README.md>`_  to apply the patch to the codebase.


**For an AVRS integration please follow below steps as well**:


1. Create an environment file called avrs-environment.yaml in usr/share/openstack-tripleo-heat-templates/environments/.

::

    FastPathMask           =====>    FP_MASK
    FastPathNics           =====>    FP_PORTS
    CorePortMapping        =====>    CORE_PORT_MAPPING
    FastPathMemory         =====>    FP_MEMORY
    VmMemory               =====>    VM_MEMORY
    NbMbuf                 =====>    NB_MBUF
    FastPathOffload        =====>    FP_OFFLOAD
    FastPathNicDescriptors =====>    FPNSDK_OPTIONS
    FastPathDPVI           =====>    DPVI_MASK
    FastPathOptions        =====>    FP_OPTIONS


2. Use the ``create_compute_avrs_role.sh`` to create a roles file called ``avrs-role.yaml``. Copy the script from `here
<https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/blob/OSPD13/avrs/create_compute_avrs_role.sh>`_  to ``/home/stack/templates/`` on Undercloud Node. Run using

::

    ./create_compute_avrs_role.sh

Above command will create a new ``ComputeAvrs``  role for your deployment, and compare it with sample avrs-role.yaml provided at https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/avrs/avrs-role.yaml .
(Please Note, given ``avrs-role.yaml`` file can get updated with newer release )


Phase 4: Generate a CMS ID for the OpenStack installation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Cloud Management System (CMS) ID needs to be generated to configure your OpenStack installation with the VSD installation.

Go to https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/generate-cms-id for the files and script to generate the CMS ID, and follow the instructions in README.md.

The CMS ID is displayed in the output, and a copy of it is stored in a file called cms_id.txt in the same folder.

Add the CMS ID to the neutron-nuage-config.yaml template file for the ``NeutronNuageCMSId`` parameter.


Phase 5: Configure the basic Overcloud.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Follow the upstream OpenStack documentation *up to the step where* the ``openstack overcloud deploy`` command is run using the CLI or starting the Overcloud deployment (starting the Overcloud creation) in the UI.

These are the OpenStack instructions:

    * Configuring the container registry details: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/configuring-a-container-image-source
    * Using the CLI: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/chap-configuring_basic_overcloud_requirements_with_the_cli_tools
    * Using the UI: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/chap-configuring_basic_overcloud_requirements_with_the_ui_tools


Phase 6: Check the Ironic node status to ensure that the Ironic nodes have been successfully created.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following commands.

1. Run the following command. The results should show the *Provisioning State* status as *available* and the *Maintenance* status as *False*.

::

    openstack baremetal node list


2. If profiles are being set for a specific placement in the deployment, run the following command. The results should show the *Provisioning State* status as *available* and the *Current Profile* status as *control* or *compute*.

::

    openstack overcloud profiles list


Phase 7: Create the Heat templates.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to /usr/share/openstack-tripleo-heat-templates/environments/ on the Undercloud machine.

2. Create these templates, and add the values for the VSD IP, CMS ID, and other parameters in the following files. Go to the `Parameters in the Heat Templates`_ section for details about the parameters in the templates.

    * neutron-nuage-config.yaml - Add the generated ``cms_id`` to the ``NeutronNuageCMSId`` parameter.
    * nova-nuage-config.yaml

3. Create the environment file ``node-info.yaml` under ``/home/stack/templates/`` to specify the count and flavor for ``Controller`` and ``Compute`` roles.

  The syntax for ``node-info.yaml`` is:

::

    parameter_defaults:
      Overcloud<Role Name from the roles file>Flavor: <flavor name>
      <Role Name from the roles file>Count: <number of nodes for this role>



This example shows how to create a deployment with one Controller node and two Compute nodes.

::

    OvercloudControllerFlavor: control
    ControllerCount: 1
    OvercloudComputeFlavor: compute
    ComputeCount: 2



For AVRS integration, follow these steps:

:Step 1: Create a flavor and profile for computeavrs:

::

    openstack flavor create --id auto --ram 4096 --disk 40 --vcpus 1 computeavrs
    openstack flavor set --property "cpu_arch"="x86_64" --property "capabilities:boot_option"="local" --property "capabilities:profile"="computeavrs" computeavrs


:Step 2: Assign AVRS nodes with a computeavrs profile:

::

    openstack baremetal node set --property capabilities='profile:computeavrs,boot_option:local' <node-uuid>


:Step 3: Add the count and flavor for ComputeAvrs Role in the node-info.yaml file. The following example shows how to create a deployment with one Controller node, two Compute nodes, and two ComputeAvrs nodes:

::

    OvercloudControllerFlavor: control
    ControllerCount: 1
    OvercloudComputeFlavor: compute
    ComputeCount: 2
    OvercloudComputeAvrsFlavor: computeavrs
    ComputeAvrsCount: 2

4. **(Optional)** To enable SR-IOV, perform the following instructions:

  This feature allows an OpenStack installation to support Single Root I/O Virtualization (SR-IOV)-attached VMs (https://wiki.openstack.org/wiki/SR-IOV-Passthrough-For-Networking) with VSP-managed VMs on the same KVM hypervisor cluster. It provides a Nuage ML2 mechanism driver that coexists with the sriovnicswitch mechanism driver.

  Neutron ports attached through SR-IOV are configured by the sriovnicswitch mechanism driver. Neutron ports attached to Nuage VSD-managed networks are configured by the Nuage ML2 mechanism driver.

  To enable SR-IOV, perform the following steps:

:Step 1: When updating the Undercloud codebase, no additional changes are required.

:Step 2: When modifying the overcloud-full image", use the script provided to update the image. No additional changes are required.

:Step 3: Create a new sriov-role.yaml file to deploy SR-IOV Compute nodes. The command used to create this file is:

::

    openstack overcloud roles generate Controller Compute ComputeSriov -o /home/stack/templates/sriov-role.yaml


:Step 4: If deploying OpenStack Neutron SR-IOV in your overcloud, include the ``/usr/share/openstack-tripleo-heat-templates/environments/services-docker/neutron-sriov.yaml`` environment file so the director can prepare the images. When following **Phase 8 Step 4** please include below environment. The following snippet is an example on how to include this environment file:

::

    openstack overcloud container image prepare \
    ...
    -e /usr/share/openstack-tripleo-heat-templates/environments/services-docker/neutron-sriov.yaml \
    ...


:Step 5: Create a flavor and profile for computesriov:

      Please refer: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/chap-configuring_basic_overcloud_requirements_with_the_cli_tools#sect-Tagging_Nodes_into_Profiles for more information.

::

    openstack flavor create --id auto --ram 4096 --disk 40 --vcpus 1 computesriov
    openstack flavor set --property "cpu_arch"="x86_64" --property "capabilities:boot_option"="local" --property "capabilities:profile"="computesriov" computesriov



:Step 6: Assign SR-IOV nodes with the appropriate computesriov profile:

::

    openstack baremetal node set --property capabilities='profile:computesriov,boot_option:local' <node-uuid>


:Step 7: Add the count and flavor for ComputeSriov Role in the node-info.yaml file. The following example shows how to create a deployment with one Controller node, two Compute nodes, and two ComputeSriov nodes:

::

    OvercloudControllerFlavor: control
    ControllerCount: 1
    OvercloudComputeFlavor: compute
    ComputeCount: 2
    OvercloudComputeSriovFlavor: computesriov
    ComputeAvrsCount: 2


:Step 8: To deploy the Overcloud, additional parameters and template files are required.

    * Include the following parameter values in the heat template neutron-nuage-config.yaml:
    
    ::
    
         NeutronServicePlugins: 'NuagePortAttributes,NuageAPI,NuageL3,trunk,NuageNetTopology'
         NeutronTypeDrivers: "vlan,vxlan,flat"
         NeutronMechanismDrivers: ['nuage','nuage_sriov','sriovnicswitch']
         NeutronFlatNetworks: '*'
         NeutronTunnelIdRanges: "1:1000"
         NeutronNetworkVLANRanges: "physnet1:2:100,physnet2:2:100"
         NeutronVniRanges: "1001:2000"
    
    
    * Add this parameter value in the heat template nova-nuage-config.yaml:
    
    ::
    
        NovaPCIPassthrough: "[{"devname":"eno2","physical_network":"physnet1"},{"devname":"eno3","physical_network":"physnet2"}]"
    
    
    * Include "neutron-sriov.yaml" file in the Overcloud deployment command. See the sample in the "Sample Templates" section.


5. **(Optional)** To enable Linux bonding with VLANs, perform the following instructions:

  Edit network-environment.j2.yaml file in /usr/share/openstack-tripleo-heat-templates/environments/. See the sample in the "Sample Templates" section.

  Nuage uses the default Linux bridge and Linux bonds. For this to take effect, modify this network file with the following required changes:

::

    /usr/share/openstack-tripleo-heat-templates/network/config/bond-with-vlans/role.role.j2.yaml


:Step 1: Remove ovs_bridge and move the containing members one level up.

:Step 2: Change ovs_bond to linux_bond with the right bonding_options (for example, bonding_options: 'mode=active-backup').

:Step 3: Change the interface names under network_config and linux_bond to the interface names of the bare metal machines that are being used.

:Step 4: Add the ``device`` option to the VLANs. This is an example for /usr/share/openstack-tripleo-heat-templates/network/config/bond-with-vlans/role.role.j2.yaml:

::

    ========
    Original
    ========
    resources:
      OsNetConfigImpl:
        type: OS::Heat::SoftwareConfig
        properties:
          group: script
          config:
            str_replace:
              template:
                get_file: ../../scripts/run-os-net-config.sh
              params:
                $network_config:
                  network_config:
                  - type: interface
                    name: nic1
                    use_dhcp: false
                    addresses:
                    - ip_netmask:
                        list_join:
                        - /
                        - - get_param: ControlPlaneIp
                          - get_param: ControlPlaneSubnetCidr
                    routes:
                    - ip_netmask: 169.254.169.254/32
                      next_hop:
                        get_param: EC2MetadataIp
    {%- if role.default_route_networks is not defined or 'ControlPlane' in role.default_route_networks %}
                    - default: true
                      next_hop:
                        get_param: ControlPlaneDefaultRoute
    {%- endif %}
    {%- if role.name != 'ComputeOvsDpdk' %}
                  - type: ovs_bridge
                    name: bridge_name
                    dns_servers:
                      get_param: DnsServers
                    members:
                    - type: ovs_bond
                      name: bond1
                      ovs_options:
                        get_param: BondInterfaceOvsOptions
                      members:
                      - type: interface
                        name: nic2
                        primary: true
                      - type: interface
                        name: nic3
    {%- for network in networks if network.enabled|default(true) and network.name in role.networks %}
                    - type: vlan
                      vlan_id:
                        get_param: {{network.name}}NetworkVlanID
                      addresses:
                      - ip_netmask:
                          get_param: {{network.name}}IpSubnet
    {%- if network.name in role.default_route_networks %}
                      routes:
                      - default: true
                        next_hop:
                          get_param: {{network.name}}InterfaceDefaultRoute
    {%- endif %}
    
    ==================================
    Modified (changes are **marked**)
    ==================================
    resources:
      OsNetConfigImpl:
        type: OS::Heat::SoftwareConfig
        properties:
          group: script
          config:
            str_replace:
              template:
                get_file: ../../scripts/run-os-net-config.sh
              params:
                $network_config:
                  network_config:
                  - type: interface
                    name: **eno1**
                    use_dhcp: false
                    addresses:
                    - ip_netmask:
                        list_join:
                        - /
                        - - get_param: ControlPlaneIp
                          - get_param: ControlPlaneSubnetCidr
                    routes:
                    - ip_netmask: 169.254.169.254/32
                      next_hop:
                        get_param: EC2MetadataIp
    {%- if role.default_route_networks is not defined or 'ControlPlane' in role.default_route_networks %}
                    - default: true
                      next_hop:
                        get_param: ControlPlaneDefaultRoute
    {%- endif %}
    {%- if role.name != 'ComputeOvsDpdk' %}
                  - type: **linux_bond**
                    name: bond1
                    dns_servers:
                      get_param: DnsServers
                  **bonding_options: 'mode=active-backup'**
                    members:
                    - type: interface
                      name: **eno2**
                      primary: true
                    - type: interface
                      name: **eno3**
    {%- for network in networks if network.enabled|default(true) and network.name in role.networks %}
                  - type: vlan
                  **device: bond1**
                    vlan_id:
                      get_param: {{network.name}}NetworkVlanID
                    addresses:
                    - ip_netmask:
                        get_param: {{network.name}}IpSubnet
    {%- if network.name in role.default_route_networks %}
                    routes:
                    - default: true
                      next_hop:
                        get_param: {{network.name}}InterfaceDefaultRoute
    {%- endif %}
    {%- endfor %}



In OSPD 9 and later, a verification step was added where the Overcloud nodes ping the gateway to verify connectivity on the external network VLAN. Without this verification step, the deployment, such as one with Linux bonding and network isolation, would fail. For this verification step, the ExternalInterfaceDefaultRoute IP configured in the template network-environment.yaml should be reachable from the Overcloud Controller nodes on the external API VLAN. This gateway can also reside on the Undercloud. The gateway needs to be tagged with the same VLAN ID as that of the external API network of the Controller.

In OSPD 13 and later, /usr/share/openstack-tripleo-heat-templates/environments/network-environment.j2.yaml gets the Network information for all the networks from /usr/share/openstack-tripleo-heat-templates/network_data.yaml file.

.. Note:: ExternalInterfaceDefaultRoute IP should be able to reach outside because the Overcloud Controller uses this IP address as a default route to reach the Red Hat Registry to pull the Overcloud container images.


6. Please follow **Phase 6** steps again for verfication of all the nodes are assigned with correct flavors.



Phase 8: Build the Docker images.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. On the Undercloud, create a directory named *Nuage-OSPD-Dockerfiles*.

2. Copy all the Docker files and the nuage.repo file from https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/nuage-ospd13-dockerfiles to the Nuage-OSPD-Dockerfiles directory.

3. For the AVRS integration, copy the nova-compute-avrs-dockerfile file and nuage_6wind.repo from https://gitlab.us.alcatel-lucent.com/nuagenetworks/nuage-ospdirector/tree/OSPD13/nuage-ospd13-dockerfiles/avrs to the Nuage-OSPD-Dockerfiles directory.

4. Configure the Overcloud to use one of the registry methods: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/configuring-a-container-image-source.

5. Use above registry document to generate the ``/home/stack/templates/overcloud_images.yaml`` environment file, which has the container image locations.

6. Get the <tag> to which the container images point:

::

    DockerHeatApiCfnImage: registry.access.redhat.com/rhosp13/openstack-heat-api-cfn:<tag>
    Example:
    DockerHeatApiCfnImage: registry.access.redhat.com/rhosp13/openstack-heat-api-cfn:13.0-60.1543534138

    DockerHeatApiImage: registry.access.redhat.com/rhosp13/openstack-heat-api:<tag>
    Example:
    DockerHeatApiImage: registry.access.redhat.com/rhosp13/openstack-heat-api:13.0-61.1543534111

    DockerHeatEngineImage: registry.access.redhat.com/rhosp13/openstack-heat-engine:<tag>
    Example:
    DockerHeatEngineImage: registry.access.redhat.com/rhosp13/openstack-heat-engine:13.0-60.1543534138

    DockerHorizonImage: registry.access.redhat.com/rhosp13/openstack-horizon:<tag>
    Example:
    DockerHorizonImage: registry.access.redhat.com/rhosp13/openstack-horizon:13.0-60.1543534103

    DockerNeutronConfigImage: registry.access.redhat.com/rhosp13/openstack-neutron-server:<tag>
    Example:
    DockerNeutronConfigImage: registry.access.redhat.com/rhosp13/openstack-neutron-server:13.0-60.1543534138
    
    # AVRS Integration
    DockerNovaComputeImage: registry.access.redhat.com/rhosp13/openstack-nova-compute:<tag>
    Example:
    DockerNovaComputeImage: registry.access.redhat.com/rhosp13/openstack-nova-compute:13.0-72



7. For all the Docker files in the Nuage-OSPD-Dockerfiles directory, change the ``<tag>`` of the Docker base image to point to the same tag in ``/home/stack/templates/overcloud_images.yaml`` .

::

    FROM <docker-image-name>:<tag>
    Example:
    FROM registry.access.redhat.com/rhosp13/openstack-neutron-server:13.0-60.1543534138


8. For all the Docker files in the Nuage-OSPD-Dockerfiles directory, provide the label that is being used on your setup.

::

    LABEL name="<undercloud-ip>:8787/rhosp13/openstack-nuage-neutron-server"
    Example:
    LABEL name="192.168.24.1:8787/rhosp13/openstack-nuage-neutron-server"


9. Set the baseurl in nuage.repo to point to the URL of the Nuage repository that hosts all of the required Nuage packages.

::

    baseurl = <baseurl>


10. For the AVRS integration, set the baseurl in nuage_6wind.repo to point to the URL of the Nuage repository that hosts all of the required 6wind and AVRS packages.

11. Build the Nuage Docker images from Nuage-OSPD-Dockerfiles directory:

::

    By default on undercloud, local registry will be listening on port 8787.
    Let us consider Undercloud IP as 192.168.24.1

    #For Nuage Heat Engine
    docker build -t <undercloud-ip>:8787/rhosp13/openstack-nuage-heat-engine:<tag> -f nuage-heat-engine-dockerfile .

    Example:
    docker build -t 192.168.24.1:8787/rhosp13/openstack-nuage-heat-engine:<tag> -f nuage-heat-engine-dockerfile .

    #For Nuage Heat API and Heat API Cron because both these services point to the same docker image
    docker build -t <undercloud-ip>:8787/rhosp13/openstack-nuage-heat-api:<tag> -f nuage-heat-api-dockerfile .

    Example:
    docker build -t 192.168.24.1:8787/rhosp13/openstack-nuage-heat-api:<tag> -f nuage-heat-api-dockerfile .

    #For Nuage Heat API-CFN
    docker build -t <undercloud-ip>:8787/rhosp13/openstack-nuage-heat-api-cfn:<tag> -f nuage-heat-api-cfn-dockerfile .

    Example:
    docker build -t 192.168.24.1:8787/rhosp13/openstack-nuage-heat-api-cfn:<tag> -f nuage-heat-api-cfn-dockerfile .

    #For Nuage Horizon
    docker build -t <undercloud-ip>:8787/rhosp13/openstack-nuage-horizon:<tag> -f nuage-horizon-dockerfile .

    Example:
    docker build -t 192.168.24.1:8787/rhosp13/openstack-nuage-horizon:<tag> -f nuage-horizon-dockerfile .

    #For Nuage Neutron
    docker build -t <undercloud-ip>:8787/rhosp13/openstack-nuage-neutron-server:<tag> -f nuage-neutron-server-dockerfile .

    Example:
    docker build -t 192.168.24.1:8787/rhosp13/openstack-nuage-neutron-server:<tag> -f nuage-neutron-server-dockerfile .

    # AVRS integration
    docker build -t <undercloud-ip>:8787/rhosp13/openstack-nuage-nova-compute-avrs:<tag> -f nova-compute-avrs-dockerfile .

    Example:
    docker build -t 192.168.24.1:8787/rhosp13/openstack-nuage-nova-compute-avrs:<tag> -f nova-compute-avrs-dockerfile .


12. During the deployment, configure the Overcloud to use the Nuage container images instead of the Red Hat registry images by pushing the build Nuage container images to the local registry.

::

    docker push 192.168.24.1:8787/rhosp13/openstack-nuage-heat-engine:<tag>
    docker push 192.168.24.1:8787/rhosp13/openstack-nuage-heat-api:<tag>
    docker push 192.168.24.1:8787/rhosp13/openstack-nuage-heat-api-cfn:<tag>
    docker push 192.168.24.1:8787/rhosp13/openstack-nuage-horizon:<tag>
    docker push 192.168.24.1:8787/rhosp13/openstack-nuage-neutron-server:<tag>


13. During the AVRS deployment, also configure the Overcloud to use the Nuage AVRS container images:

::

    docker push 192.168.24.1:8787/rhosp13/openstack-nuage-nova-compute-avrs:<tag>


14. Change the /home/stack/templates/overcloud_images.yaml file to point Heat, Horizon, Neutron, and their Docker configuration images to ones in the local registry:

::

    DockerHeatApiCfnConfigImage: 192.168.24.1:8787/rhosp13/openstack-nuage-heat-api-cfn:<tag>
    DockerHeatApiCfnImage: 192.168.24.1:8787/rhosp13/openstack-nuage-heat-api-cfn:<tag>
    DockerHeatApiConfigImage: 192.168.24.1:8787/rhosp13/openstack-nuage-heat-api:<tag>
    DockerHeatApiImage: 192.168.24.1:8787/rhosp13/openstack-nuage-heat-api:<tag>
    DockerHeatConfigImage: 192.168.24.1:8787/rhosp13/openstack-nuage-heat-api:<tag>
    DockerHeatEngineImage: 192.168.24.1:8787/rhosp13/openstack-nuage-heat-engine:<tag>
    DockerHorizonConfigImage: 192.168.24.1:8787/rhosp13/openstack-nuage-horizon:<tag>
    DockerHorizonImage: 192.168.24.1:8787/rhosp13/openstack-nuage-horizon:<tag>
    DockerNeutronApiImage: 192.168.24.1:8787/rhosp13/openstack-nuage-neutron-server:<tag>
    DockerNeutronConfigImage: 192.168.24.1:8787/rhosp13/openstack-nuage-neutron-server:<tag>


15. For AVRS integration, change the /home/stack/templates/overcloud_images.yaml file and add the following parameters to point the AVRS Docker images to ones in the local registry:

::

    DockerNovaComputeAvrsImage: 192.168.24.1:8787/rhosp13/openstack-nuage-nova-compute-avrs:<tag>
    DockerNovaLibvirtAvrsConfigImage: 192.168.24.1:8787/rhosp13/openstack-nuage-nova-compute-avrs:<tag>


Phase 9: Deploy the Overcloud.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the Heat templates with the the command-line based template to deploy the Overcloud.

Use the ``openstack overcloud deploy`` command options to pass the environment files and to create or update an Overcloud deployment where:

    * docker-insecure-registry.yaml has IP and port values for the Insecure Registry parameter.
    * neutron-nuage-config.yaml has the Nuage-specific Controller parameter values.
    * node-info.yaml has information specifying the count and flavor for the Controller and Compute nodes.
    * nova-nuage-config.yaml has the Nuage-specific Compute parameter values.

For AVRS, also include following role and environment files.

    * avrs-role.yaml
    * avrs-environment.yaml


1. For a non-HA Overcloud deployment, use one of the following commands:

::

    openstack overcloud deploy --templates -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/templates/docker-insecure-registry.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server
    
    For a virtual deployment, add the --libvirt-type parameter:
    openstack overcloud deploy --templates --libvirt-type qemu -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/templates/docker-insecure-registry.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server
    
    For AVRS integration, use:
    openstack overcloud deploy --templates -r /home/stack/templates/avrs-role.yaml -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/templates/docker-insecure-registry.yaml  -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/avrs-environment.yaml


2. For an HA deployment, use one of the following commands:

::

    openstack overcloud deploy --templates -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/templates/docker-insecure-registry.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server
    
    For a virtual deployment, add the --libvirt-type parameter:
    openstack overcloud deploy --templates --libvirt-type qemu -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/templates/docker-insecure-registry.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server
    
    For AVRS integration, use:
    openstack overcloud deploy --templates -r /home/stack/templates/avrs-role.yaml -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/templates/docker-insecure-registry.yaml  -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/avrs-environment.yaml


3. For SR-IOV, use following commands:

::

   openstack overcloud deploy --templates -r /home/stack/templates/sriov-role.yaml -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/docker-insecure-registry.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/templates/neutron-sriov.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server


4. For a Linux-bonding HA deployment with Nuage, use the following:

::

    openstack overcloud deploy --templates -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/docker-insecure-registry.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/network-environment.yaml -e /home/stack/templates/node-info.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/network-isolation.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/net-bond-with-vlans.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server

    For AVRS integration, use the following:
    openstack overcloud deploy --templates -r /home/stack/templates/avrs-role.yaml -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/docker-insecure-registry.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/network-environment.yaml -e /home/stack/templates/node-info.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/network-isolation.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/net-bond-with-vlans.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/avrs-environment.yaml --ntp-server ntp-server


where:
   * ``neutron-nuage-config.yaml`` is Controller specific parameter values.
   * ``nova-nuage-config.yaml`` is Compute specific parameter values.
   * ``docker-insecure-registry.yaml`` contains all local registry IPs and Ports for Insecure Registry parameter.
   * ``node-info.yaml`` is Information specifies count and flavor for Controller and Compute nodes.
   * ``network-environment.yaml`` Configures additional network environment variables
   * ``network-isolation.yaml`` Enables creation of networks for isolated overcloud traffic
   * ``net-bond-with-vlans.yaml`` Configures an IP address and a pair of bonded nics on each network
   * ``sriov-role.yaml`` Enables services required for Compute Sriov role
   * ``neutron-sriov.yaml`` Neutron SRIOV specific parameter values
   * ``avrs-role.yaml`` Enables services required for Compute Avrs role




Phase 10: Verify that OpenStack director has been deployed successfully.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Run ``openstack stack list`` to verify that the stack was created.

::

    [stack@director ~]$ openstack stack list

    +--------------------------------------+------------+----------------------------------+-----------------+----------------------+-----------------+
    | ID                                   | Stack Name | Project                          | Stack Status    | Creation Time        | Updated Time    |
    +--------------------------------------+------------+----------------------------------+-----------------+----------------------+-----------------+
    | 75810b99-c372-463c-8684-f0d7b4e5743e | overcloud  | 1c60ab81cc924fe78355a76ee362386b | CREATE_COMPLETE | 2018-03-27T07:26:28Z | None            |
    +--------------------------------------+------------+----------------------------------+-----------------+----------------------+-----------------+


2. Run ``nova list`` to view the Overcloud Compute and Controller nodes.

::

    [stack@director ~]$ nova list
    +--------------------------------------+------------------------+--------+------------+-------------+---------------------+
    | ID                                   | Name                   | Status | Task State | Power State | Networks            |
    +--------------------------------------+------------------------+--------+------------+-------------+---------------------+
    | 437ff73b-3615-48cc-a9cf-ed0790953577 | overcloud-compute-0    | ACTIVE | -          | Running     | ctlplane=192.0.2.60 |
    | 797e7a74-eb96-49fb-87e7-9e6955e70c70 | overcloud-compute-1    | ACTIVE | -          | Running     | ctlplane=192.0.2.58 |
    | a7ef35db-4230-4fcd-9411-a6329f4747c9 | overcloud-compute-2    | ACTIVE | -          | Running     | ctlplane=192.0.2.59 |
    | a0548879-0931-4b2c-bbe9-2733e4566d64 | overcloud-controller-0 | ACTIVE | -          | Running     | ctlplane=192.0.2.57 |
    +--------------------------------------+------------------------+--------+------------+-------------+---------------------+


3. Verify that the services are running.


4. Check the VRS and VSC connection on an Overcloud Compute node.

::

    [heat-admin@overcloud-compute-1 ~]$ sudo ovs-vsctl show
    cc87b725-7107-4917-b239-8dea497f5624
        Bridge "alubr0"
            Controller "ctrl1"
                target: "tcp:101.0.0.21:6633"
                role: master
                is_connected: true
            Controller "ctrl2"
                target: "tcp:101.0.0.22:6633"
                role: slave
                is_connected: true
            Port "alubr0"
                Interface "alubr0"
                    type: internal
            Port svc-spat-tap
                Interface svc-spat-tap
                    type: internal
            Port svc-pat-tap
                Interface svc-pat-tap
                    type: internal
            Port "svc-rl-tap1"
                Interface "svc-rl-tap1"
            Port "svc-rl-tap2"
                Interface "svc-rl-tap2"
        ovs_version: "5.3.1-11-nuage"


Phase 11 (Optional) For SR-IOV, manually install and run the topology collector.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the detailed steps in `Installation and Configuration: Topology Collection Agent and LLDP <queens-40-using.html#installation-and-configuration-topology-collection-agent-and-lldp>`_ . 

Also see the OpenStack SR-IOV documentation for more information.


Parameters in the Heat Templates
---------------------------------

This section has the details about the parameters specified in the template files. It also describes the configuration files where the parameters are set and used.

Go to http://docs.openstack.org/developer/heat/template_guide/hot_guide.html and https://docs.openstack.org/queens/configuration/ for more information.


Parameters on the Neutron Controller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following parameters are mapped to values in the /etc/neutron/plugins/nuage/plugin.ini file on the Neutron controller:

::

    NeutronNuageNetPartitionName
    Maps to default_net_partition_name parameter

    NeutronNuageVSDIp
    Maps to server parameter

    NeutronNuageVSDUsername
    NeutronNuageVSDPassword
    Maps to serverauth as username:password

    NeutronNuageVSDOrganization
    Maps to organization parameter

    NeutronNuageBaseURIVersion
    Maps to the version in base_uri as /nuage/api/<version>

    NeutronNuageCMSId
    Maps to the cms_id parameter


The following parameters are mapped to values in the /etc/neutron/neutron.conf file on the Neutron controller:

::

    NeutronCorePlugin
    Maps to core_plugin parameter in [DEFAULT] section

    NeutronServicePlugins
    Maps to service_plugins parameter in [DEFAULT] section


The following parameters are mapped to values in the /etc/nova/nova.conf file on the Neutron controller:

::

    UseForwardedFor
    Maps to use_forwarded_for parameter in [DEFAULT] section

    NeutronMetadataProxySharedSecret
    Maps to metadata_proxy_shared_secret parameter in [neutron] section

    InstanceNameTemplate
    Maps to instance_name_template parameter in [DEFAULT] section


The following parameters are mapped to values in the /etc/neutron/plugins/ml2/ml2_conf.ini file on the Neutron controller:

::

    NeutronNetworkType
    Maps to tenant_network_types in [ml2] section

    NeutronPluginExtensions
    Maps to extension_drivers in [ml2] section

    NeutronTypeDrivers
    Maps to type_drivers in [ml2] section

    NeutronMechanismDrivers
    Maps to mechanism_drivers in [ml2] section

    NeutronFlatNetworks
    Maps to flat_networks parameter in [ml2_type_flat] section

    NeutronTunnelIdRanges
    Maps to tunnel_id_ranges in [ml2_type_gre] section

    NeutronNetworkVLANRanges
    Maps to network_vlan_ranges in [ml2_type_vlan] section

    NeutronVniRanges
    Maps to vni_ranges in [ml2_type_vxlan] section


The following parameter is mapped to value in the /etc/heat/heat.conf file on the controller:

::

    HeatEnginePluginDirs
    Maps to plugin_dirs in [DEFAULT] section


The following parameter is mapped to value in the /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py on controller

::

    HorizonCustomizationModule
    Maps to customization_module in HORIZON_CONFIG dict


The following parameter is mapped to value in the /etc/httpd/conf.d/10-horizon_vhost.conf on controller

::

    HorizonVhostExtraParams
    Maps to CustomLog, Alias in this file


The following parameters are used to set and/or disable services in the Undercloud Puppet code:

::

    OS::TripleO::Services::NeutronDHCPAgent
    OS::TripleO::Services::NeutronL3Agent
    OS::TripleO::Services::NeutronMetadataAgent
    OS::TripleO::Services::NeutronOVSAgent
    These parameters are used to disable the OpenStack default services as these are not used with Nuage integrated OpenStack cluster


The following parameter is to set values on the Controller using Puppet code:

::

    NeutronNuageDBSyncExtraParams
    String of extra command line parameters to append to the neutron-db-manage upgrade head command


Parameters on the Nova Compute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following parameters are mapped to values in the /etc/default/openvswitch file on the Nova Compute:

::

    NuageActiveController
    Maps to ACTIVE_CONTROLLER parameter

    NuageStandbyController
    Maps to STANDBY_CONTROLLER parameter


The following parameters are mapped to values in the /etc/nova/nova.conf file on the Nova Compute:

::

    NovaOVSBridge
    Maps to ovs_bridge parameter in [neutron] section

    NovaComputeLibvirtType
    Maps to virt_type parameter in [libvirt] section

    NovaIPv6
    Maps to use_ipv6 in [DEFAULT] section


The following parameters are mapped to values in the /etc/default/nuage-metadata-agent file on the Nova Compute:

::

    NuageMetadataProxySharedSecret
    Maps to METADATA_PROXY_SHARED_SECRET parameter. This need to match the setting in neutron controller above

    NuageNovaApiEndpoint
    Maps to NOVA_API_ENDPOINT_TYPE parameter. This needs to correspond to  the setting for the Nova API endpoint as configured by OSP Director


Parameters Required for Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This parameter is required:

::

    DockerInsecureRegistryAddress
    The IP Address and Port of an insecure docker namespace that will be configured in /etc/sysconfig/docker.
    The value can be multiple addresses separated by commas.


Sample Templates
-----------------

For the latest templates, go to the `Links to Nuage and OpenStack Resources`_ section.


network-environment.j2.yaml
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    #This file is an example of an environment file for defining the isolated
    #networks and related parameters.
    resource_registry:
      # Network Interface templates to use (these files must exist). You can
      # override these by including one of the net-*.yaml environment files,
      # such as net-bond-with-vlans.yaml, or modifying the list here.
    {%- for role in roles %}
      # Port assignments for the {{role.name}}
      OS::TripleO::{{role.name}}::Net::SoftwareConfig:
        ../network/config/bond-with-vlans/{{role.deprecated_nic_config_name|default(role.name.lower() ~ ".yaml")}}
    {%- endfor %}

    parameter_defaults:
      # This section is where deployment-specific configuration is done
      # CIDR subnet mask length for provisioning network
      ControlPlaneSubnetCidr: '24'
      # Gateway router for the provisioning network (or Undercloud IP)
      ControlPlaneDefaultRoute: 192.168.24.1
      EC2MetadataIp: 192.168.24.1  # Generally the IP of the Undercloud
      # Customize the IP subnets to match the local environment
    {%- for network in networks if network.enabled|default(true) %}
    {%- if network.ipv6|default(false) %}
      {{network.name}}NetCidr: '{{network.ipv6_subnet}}'
    {%- else %}
      {{network.name}}NetCidr: '{{network.ip_subnet}}'
    {%- endif %}
    {%- endfor %}
      # Customize the VLAN IDs to match the local environment
    {%- for network in networks if network.enabled|default(true) %}
    {%- if network.vlan is defined %}
      {{network.name}}NetworkVlanID: {{network.vlan}}
    {%- endif %}
    {%- endfor %}
    {%- for network in networks if network.enabled|default(true) %}
    {%- if network.name == 'External' %}
      # Leave room if the external network is also used for floating IPs
    {%- endif %}
    {%- if network.ipv6|default(false) %}
      {{network.name}}AllocationPools: {{network.ipv6_allocation_pools}}
    {%- else %}
      {{network.name}}AllocationPools: {{network.allocation_pools}}
    {%- endif %}
    {%- endfor %}
      # Gateway routers for routable networks
    {%- for network in networks if network.enabled|default(true) %}
    {%- if network.ipv6|default(false) and network.gateway_ipv6|default(false) %}
      {{network.name}}InterfaceDefaultRoute: '{{network.gateway_ipv6}}'
    {%- elif network.gateway_ip|default(false) %}
      {{network.name}}InterfaceDefaultRoute: '{{network.gateway_ip}}'
    {%- endif %}
    {%- endfor %}
    {#- FIXME: These global parameters should be defined in a YAML file, e.g. network_data.yaml. #}
      # Define the DNS servers (maximum 2) for the overcloud nodes
      DnsServers: ["135.1.1.111","135.227.146.166"]
      # List of Neutron network types for tenant networks (will be used in order)
      NeutronNetworkType: 'vxlan,vlan'
      # The tunnel type for the tenant network (vxlan or gre). Set to '' to disable tunneling.
      NeutronTunnelTypes: 'vxlan'
      # Neutron VLAN ranges per network, for example 'datacentre:1:499,tenant:500:1000':
      NeutronNetworkVLANRanges: 'datacentre:1:1000'
      # Customize bonding options, e.g. "mode=4 lacp_rate=1 updelay=1000 miimon=100"
      # for Linux bonds w/LACP, or "bond_mode=active-backup" for OVS active/backup.
      BondInterfaceOvsOptions: "bond_mode=active-backup"


neutron-nuage-config.yaml
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # A Heat environment file which can be used to enable a
    # a Neutron Nuage backend on the controller, configured via puppet
    resource_registry:
      OS::TripleO::Services::NeutronDhcpAgent: OS::Heat::None
      OS::TripleO::Services::NeutronL3Agent: OS::Heat::None
      OS::TripleO::Services::NeutronMetadataAgent: OS::Heat::None
      OS::TripleO::Services::NeutronOvsAgent: OS::Heat::None
      OS::TripleO::Services::ComputeNeutronOvsAgent: OS::Heat::None
      # Override the NeutronCorePlugin to use Nuage
      OS::TripleO::Docker::NeutronMl2PluginBase: OS::TripleO::Services::NeutronCorePluginML2Nuage

    parameter_defaults:
      NeutronNuageNetPartitionName: 'Nuage_Partition_13'
      NeutronNuageVSDIp: '192.168.24.118:8443'
      NeutronNuageVSDUsername: 'csproot'
      NeutronNuageVSDPassword: 'csproot'
      NeutronNuageVSDOrganization: 'csp'
      NeutronNuageBaseURIVersion: 'v5_0'
      NeutronNuageCMSId: 'a91a28b8-28de-436b-a665-6d08a9346464'
      UseForwardedFor: true
      NeutronPluginMl2PuppetTags: 'neutron_plugin_ml2,neutron_plugin_nuage'
      NeutronServicePlugins: 'NuagePortAttributes,NuageAPI,NuageL3'
      NeutronDBSyncExtraParams: '--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --config-file /etc/neutron/plugins/nuage/plugin.ini'
      NeutronTypeDrivers: 'vxlan'
      NeutronNetworkType: 'vxlan'
      NeutronMechanismDrivers: 'nuage'
      NeutronPluginExtensions: 'nuage_subnet,nuage_port,port_security'
      NeutronFlatNetworks: '*'
      NeutronTunnelIdRanges: ''
      NeutronNetworkVLANRanges: ''
      NeutronVniRanges: '1001:2000'
      NovaOVSBridge: 'alubr0'
      NeutronMetadataProxySharedSecret: 'NuageNetworksSharedSecret'
      InstanceNameTemplate: 'inst-%08x'
      HeatEnginePluginDirs: ['/usr/lib/python2.7/site-packages/nuage-heat/']
      HorizonCustomizationModule: 'nuage_horizon.customization'
      HorizonVhostExtraParams:
        add_listen: true
        priority: 10
        access_log_format: '%a %l %u %t \"%r\" %>s %b \"%%{}{Referer}i\" \"%%{}{User-Agent}i\"'
        aliases: [{'alias': '%{root_url}/static/nuage', 'path': '/usr/lib/python2.7/site-packages/nuage_horizon/static'}, {'alias': '%{root_url}/static', 'path': '/usr/share/openstack-dashboard/static'}]
        directories: [{'path': '/usr/lib/python2.7/site-packages/nuage_horizon', 'options': ['FollowSymLinks'], 'allow_override': ['None'], 'require': 'all granted'}]


neutron-sriov.yaml
~~~~~~~~~~~~~~~~~~~

Include this file in the ``openstack overcloud deploy`` command when you deploy the Overcloud:

::

    ## A Heat environment that can be used to deploy SR-IOV
    resource_registry:
      OS::TripleO::Services::NeutronSriovAgent: /usr/share/openstack-tripleo-heat-templates/docker/services/neutron-sriov-agent.yaml
      OS::TripleO::Services::NeutronSriovHostConfig: /usr/share/openstack-tripleo-heat-templates/puppet/services/neutron-sriov-host-config.yaml

    parameter_defaults:
      # Add PciPassthroughFilter to the scheduler default filters
      NovaSchedulerDefaultFilters: ['RetryFilter','AvailabilityZoneFilter','RamFilter','ComputeFilter','ComputeCapabilitiesFilter','ImagePropertiesFilter','ServerGroupAntiAffinityFilter','ServerGroupAffinityFilter','PciPassthroughFilter']
      NovaSchedulerAvailableFilters: ['nova.scheduler.filters.all_filters']

      NeutronPhysicalDevMappings: "physnet1:eno2,physnet2:eno3"

      # Number of VFs that needs to be configured for a physical interface
      NeutronSriovNumVFs: "eno2:5,eno3:7"


nova-nuage-config.yaml For a Virtual Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # A Heat environment file which can be used to enable
    # Nuage backend on the compute, configured via puppet
    resource_registry:
      OS::TripleO::Services::ComputeNeutronCorePlugin: OS::TripleO::Services::ComputeNeutronCorePluginNuage

    parameter_defaults:
      NuageActiveController: '192.168.24.119'
      NuageStandbyController: '0.0.0.0'
      NovaPCIPassthrough: ""
      NovaOVSBridge: 'alubr0'
      NovaComputeLibvirtType: 'qemu'
      NovaIPv6: True
      NuageMetadataProxySharedSecret: 'NuageNetworksSharedSecret'
      NuageNovaApiEndpoint: 'internalURL'


nova-nuage-config.yaml For a KVM Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # A Heat environment file which can be used to enable
    # Nuage backend on the compute, configured via puppet
    resource_registry:
      OS::TripleO::Services::ComputeNeutronCorePlugin: OS::TripleO::Services::ComputeNeutronCorePluginNuage

    parameter_defaults:
      NuageActiveController: '192.168.24.119'
      NuageStandbyController: '0.0.0.0'
      NovaPCIPassthrough: ""
      NovaOVSBridge: 'alubr0'
      NovaComputeLibvirtType: 'kvm'
      NovaIPv6: True
      NuageMetadataProxySharedSecret: 'NuageNetworksSharedSecret'
      NuageNovaApiEndpoint: 'internalURL'


avrs-environment.yaml for AVRS integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    resource_registry:
      OS::TripleO::ComputeAvrs::NodeUserData: ../firstboot/avrs-first-boot.yaml
      OS::TripleO::ComputeAvrsExtraConfigPost: ../extraconfig/post_deploy/avrs-post.yaml

    parameter_defaults:
      NovaVcpuPinSet: "2-7,10-15"
      # An array of filters used by Nova to filter a node.These filters will be applied in the order they are listed,
      # so place your most restrictive filters first to make the filtering process more efficient.
      NovaSchedulerDefaultFilters: "RetryFilter,AvailabilityZoneFilter,RamFilter,ComputeFilter,ComputeCapabilitiesFilter,ImagePropertiesFilter,ServerGroupAntiAffinityFilter,ServerGroupAffinityFilter,PciPassthroughFilter,NUMATopologyFilter,AggregateInstanceExtraSpecsFilter"
      # Kernel arguments for Compute node
      ComputeKernelArgs: "hugepages=12831 iommu=pt intel_iommu=on"
      # A list or range of physical CPU cores to be tuned.
      # The given args will be appended to the tuned cpu-partitioning profile.
      HostIsolatedCoreList: "1-7,9-15"
      FastPathNics: "0000:06:00.1 0000:06:00.2"
      FastPathMask: "1,9"
      FastPathNicDescriptors: "--nb-rxd=4096 --nb-txd=4096"
      FastPathOptions: "\"--mod-opt=fp-vswitch:--flows=200000 --max-nfct=40000\""
      FastPathDPVI: "0"
      FastPathOffload: "off"


docker-insecure-registry.yaml for One Local Registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    parameter_defaults:
      DockerInsecureRegistryAddress: ['192.168.24.1:8787']


node-info.yaml for Non-HA Deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Compute and Controller count can be set here

    parameter_defaults:
      ControllerCount: 1
      ComputeCount: 1


node-info.yaml for HA and Linux-Bond HA Deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Compute and Controller count can be set here

    parameter_defaults:
      ControllerCount: 3
      ComputeCount: 1


node-info.yaml for SR-IOV Deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    parameter_defaults:
      OvercloudControllerFlavor: control
      OvercloudComputeFlavor: compute
      # OvercloudComputeSriovFlavor is the flavor to use for Compute Sriov nodes
      OvercloudComputeSriovFlavor: computesriov
      ControllerCount: 1
      ComputeCount: 1
      # ComputeSriovCount is number of Compute Sriov nodes
      ComputeSriovCount: 1


Troubleshooting
----------------

This section describes issues that may happen and how to resolve them.

One or More of the Deployed Overcloud Nodes Stop
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On the node that was shut down, enter ``nova start <node_name>``. An example of the <node_name> is overcloud-controller-0.

After the node comes up, enter these commands:

::

    pcs cluster start --all
    pcs status



If the services do not come up, enter ``pcs resource cleanup``.


While Running the Script to Patch and Modify the Overcloud qcow Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the following issue occurs:

::

    virt-customize: error: libguestfs error: could not create appliance through libvirt.

    Try running qemu directly without libvirt using this environment variable:
    export LIBGUESTFS_BACKEND=direct


Run the ``export LIBGUESTFS_BACKEND=direct`` command before executing the script.


While Registering Nodes
~~~~~~~~~~~~~~~~~~~~~~~~

The ``No valid host found`` error occurs:

::

    openstack baremetal import --json instackenv.json
    No valid host was found. Reason: No conductor service registered which supports driver pxe_ipmitool. (HTTP 404)


The workaround is to install the python-dracclient python package, and restart the Ironic-Conductor service. Then enter the command to restart the service.

::

    sudo yum install -y python-dracclient
    exit (go to root user)
    systemctl restart openstack-ironic-conductor
    su - stack (switch to stack user)
    source stackrc (source stackrc)


The *openstack baremetal node list* Output Shows the Instance UUID after Deleting the Stack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The command output is similar to the following:

::


    [stack@instack ~]$ openstack stack list

    +----+------------+--------------+---------------+--------------+
    | id | stack_name | stack_status | creation_time | updated_time |
    +----+------------+--------------+---------------+--------------+
    +----+------------+--------------+---------------+--------------+
    [stack@instack ~]$ nova list
    +----+------+--------+------------+-------------+----------+
    | ID | Name | Status | Task State | Power State | Networks |
    +----+------+--------+------------+-------------+----------+
    +----+------+--------+------------+-------------+----------+
    [stack@instack ~]$ openstack baremetal node list
    +--------------------------------------+------+--------------------------------------+-------------+--------------------+-------------+
    | UUID                                 | Name | Instance UUID                        | Power State | Provisioning State | Maintenance |
    +--------------------------------------+------+--------------------------------------+-------------+--------------------+-------------+
    | 9e57d620-3ec5-4b5e-96b1-bf56cce43411 | None | 1b7a6e50-3c15-4228-85d4-1f666a200ad5 | power off   | available          | False       |
    | 88b73085-1c8e-4b6d-bd0b-b876060e2e81 | None | 31196811-ee42-4df7-b8e2-6c83a716f5d9 | power off   | available          | False       |
    | d3ac9b50-bfe4-435b-a6f8-05545cd4a629 | None | 2b962287-6e1f-4f75-8991-46b3fa01e942 | power off   | available          | False       |
    +--------------------------------------+------+--------------------------------------+-------------+--------------------+-------------+


The workaround is to manually remove the instance_uuid reference:

::

    ironic node-update <node_uuid> remove instance_uuid

    Example:
    ironic node-update 9e57d620-3ec5-4b5e-96b1-bf56cce43411 remove instance_uuid

