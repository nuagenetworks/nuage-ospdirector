.. _rocky-80-ospd:

.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

.. NOTES do not render correctly in the GitHub Preview, BUT they do in the HTML output, so do not worry!


.. .. Date, Version and Author
.. .. ==========================
.. ..
.. ..  =========  =======    =========
.. ..  Date       Version    Author
.. ..  =========  =======    =========
.. ..  02/27/19    5.4.1     speesapa - Add doc in github


======================================================
Deploying Rocky Using OpenStack Platform Director 14
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
https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/14/html/director_installation_and_usage/ .

VSP requirements:

   * VSD and VSC are set up before running OpenStack Platform director.
   * Your network includes redundant VSDs.
   * Manual Horizon and Heat integration for Nuage Extensions are required because these modules are not part of the packaged integration.


RHEL 7.6 is supported with OSP 14.

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
    * Go to https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/14/html/director_installation_and_usage/ for more Red Hat best practices.


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
        - nuage-puppet-modules-5.1.0
        - selinux-policy-nuage

    - Uninstall Open vSwitch (OVS).
    - Install VRS (nuage-openvswitch).

    - Use nuage-puppet-modules-5.1.0.x86_64.rpm and the nuage_overcloud_full_patch.py script to patch to the Overcloud qcow image, uninstall Open vSwitch (OVS), and install VRS.


* Updating the TripleO Heat templates (also referred to as the puppet manifests)

    - Some of the parameters in ``neutron.conf`` and ``nova.conf`` need to be configured in the Heat templates. The Nuage VRS and metadata agent also need to be configured. The values for these parameters depend on the Nuage VSP configuration.
      We use ``neutron-nuage-config.yaml`` and ``nova-nuage-config.yaml`` environment files to configure these values.
    - See the `Sample Templates`_ section for some probable values of the parameters in the ``neutron-nuage-config.yaml`` and ``nova-nuage-config.yaml`` files.

* Updating the Docker Images

    Some Nuage Docker images are not in the Red Hat registry. Use the following required Docker files and instructions provided by Nuage:

    - nuage-openstack-neutron
    - nuage-openstack-neutronclient
    - nuage-openstack-horizon
    - nuage-openstack-heat

Links to Nuage and OpenStack Resources
---------------------------------------

* For the Heat templates used by OpenStack director, go to http://git.openstack.org/cgit/openstack/tripleo-heat-templates .
* For the Puppet manifests, go to http://git.openstack.org/cgit/openstack/tripleo-heat-templates/tree/puppet .
* For the nuage-puppet-modules RPM (nuage-puppet-modules-5.1.0), go to https://github.com/nuagenetworks/nuage-ospdirector/tree/OSPD14/image-patching .
* For the script to patch the Overcloud qcow image (nuage_overcloud_full_patch.py), go to https://github.com/nuagenetworks/nuage-ospdirector/tree/OSPD14/image-patching/stopgap-script/nuage_overcloud_full_patch.py .
* For the Nuage and Puppet modules, go to http://git.openstack.org/cgit/openstack/puppet-neutron .
* For the files and script to generate the CMS ID, go to https://github.com/nuagenetworks/nuage-ospdirector/tree/OSPD14/generate-cms-id .


Before the Deployment Process
------------------------------

.. Note:: Before performing the procedures in this document, read the *Director Installation and Usage* guide for OSPD 14: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/14/html/director_installation_and_usage .

Create separate repositories for the following packages:

    * OSC and VRS: `OSC and VRS Packages`_


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
    * nuage-puppet-modules (Latest version 5.1.0)
    * Selinux-policy-nuage


Deployment Process
-------------------

Phase 1: Install OpenStack director on the Undercloud system.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow the steps in https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/14/html/director_installation_and_usage/installing-the-undercloud .

When obtaining images for the Overcloud nodes, replace the upstream Overcloud image with one modified to include Nuage components from Step 2 in this workflow.


Phase 2: Modify the Overcloud qcow image (for example, overcloud-full.qcow2) to include Nuage components.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The steps for modifying overcloud-full.qcow2 are provided in the README.md file: https://github.com/nuagenetworks/nuage-ospdirector/tree/OSPD14/image-patching/stopgap-script/README.md .


Phase 3: Generate a CMS ID for the OpenStack installation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Cloud Management System (CMS) ID needs to be generated to configure your OpenStack installation with the VSD installation.

Go to https://github.com/nuagenetworks/nuage-ospdirector/tree/OSPD14/generate-cms-id for the files and script to generate the CMS ID, and follow the instructions in README.md.

The CMS ID is displayed in the output, and a copy of it is stored in a file called cms_id.txt in the same folder.

Add the CMS ID to the neutron-nuage-config.yaml template file for the ``NeutronNuageCMSId`` parameter.


Phase 4: Configure the basic Overcloud.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Follow the upstream OpenStack documentation *up to the step where* the ``openstack overcloud deploy`` command is run using the CLI or starting the Overcloud deployment (starting the Overcloud creation) in the UI.

These are the OpenStack instructions:

    * Using the CLI: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/14/html/director_installation_and_usage/creating-a-basic-overcloud-with-cli-tools
    * Using the UI: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/14/html/director_installation_and_usage/chap-configuring_basic_overcloud_requirements_with_the_ui_tools


Phase 5: Check the Ironic node status to ensure that the Ironic nodes have been successfully created.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following commands.

1. Run the following command. The results should show the *Provisioning State* status as *available* and the *Maintenance* status as *False*.

::

    openstack baremetal node list


2. If profiles are being set for a specific placement in the deployment, run the following command. The results should show the *Provisioning State* status as *available* and the *Current Profile* status as *control* or *compute*.

::

    openstack overcloud profiles list


Phase 6: Create the Heat templates.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to /usr/share/openstack-tripleo-heat-templates/environments/ on the Undercloud machine.

2. Modify these templates, and add the values for the VSD IP, CMS ID, and other parameters in the following files. Go to the `Parameters in the Heat Templates`_ section for details about the parameters in the templates.

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

4. **(Optional)** To enable Linux bonding with VLANs, perform the following instructions:

  Rename single-nic-vlans as bond-with-vlans in network-environment.j2.yaml file in /usr/share/openstack-tripleo-heat-templates/environments/. See the sample in the `Sample Templates`_ section.

  Nuage uses the default Linux bridge and Linux bonds. For this to take effect, modify this network file with the following required changes and sample with those changes is provided below:

::

    /usr/share/openstack-tripleo-heat-templates/network/config/bond-with-vlans/role.role.j2.yaml


:Step 1: Change ovs_bond to linux_bond

:Step 2: Change br-bond and bridge_name to bond1

:Step 3: Add bonding_options below dns_servers and point it to BondInterfaceOvsOptions

:Step 4: Remove ovs_bond as member and move the containing members one level up.

:Step5: Add the ``device`` option to the VLANs.

::

    ========
    Original
    ========
    {%- if not role.name.startswith('ComputeOvsDpdk') %}
                  - type: ovs_bridge
    {%- if role.name.startswith('CephStorage') or role.name.startswith('ObjectStorage') or role.name.startswith('BlockStorage') %}
                    name: br-bond
    {%- else %}
                    name: bridge_name
    {%- endif %}
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
                      routes:
                        list_concat_unique:
                          - get_param: {{network.name}}InterfaceRoutes
    {%- if network.name in role.default_route_networks %}
                          - - default: true
                              next_hop:
                                get_param: {{network.name}}InterfaceDefaultRoute

    ==================================
    Modified (changes are **marked**)
    ==================================
    {%- if not role.name.startswith('ComputeOvsDpdk') %}
                  - type: **linux_bond**
    {%- if role.name.startswith('CephStorage') or role.name.startswith('ObjectStorage') or role.name.startswith('BlockStorage') %}
                    name: **bond1**
    {%- else %}
                    name: **bond1**
    {%- endif %}
                    dns_servers:
                      get_param: DnsServers
                  **bonding_options:**
                    **get_param: BondInterfaceOvsOptions**
                    members:
                    - type: interface
                      name: nic2
                      primary: true
                    - type: interface
                      name: nic3
    {%- for network in networks if network.enabled|default(true) and network.name in role.networks %}
                  - type: vlan
                  **device: bond1**
                    vlan_id:
                      get_param: {{network.name}}NetworkVlanID
                    addresses:
                    - ip_netmask:
                        get_param: {{network.name}}IpSubnet
                    routes:
                      list_concat_unique:
                        - get_param: {{network.name}}InterfaceRoutes
    {%- if network.name in role.default_route_networks %}
                        - - default: true
                            next_hop:
                              get_param: {{network.name}}InterfaceDefaultRoute


In OSPD 9 and later, a verification step was added where the Overcloud nodes ping the gateway to verify connectivity on the external network VLAN. Without this verification step, the deployment, such as one with Linux bonding and network isolation, would fail. For this verification step, the ExternalInterfaceDefaultRoute IP configured in the template network-environment.yaml should be reachable from the Overcloud Controller nodes on the external API VLAN. This gateway can also reside on the Undercloud. The gateway needs to be tagged with the same VLAN ID as that of the external API network of the Controller.

In OSPD 13 and later, /usr/share/openstack-tripleo-heat-templates/environments/network-environment.j2.yaml gets the Network information for all the networks from /usr/share/openstack-tripleo-heat-templates/network_data.yaml file.

.. Note:: ExternalInterfaceDefaultRoute IP should be able to reach outside because the Overcloud Controller uses this IP address as a default route to reach the Red Hat Registry to pull the Overcloud container images.



Phase 7: Nuage Docker images.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. On the Undercloud, use the following instructions to get Nuage images from a Red Hat container registry using registry service account tokens. You will need to `create a registry service account <https://access.redhat.com/terms-based-registry>`_ to use prior to completing the following task.

::

    $ docker login registry.connect.redhat.com
    Username: ${REGISTRY-SERVICE-ACCOUNT-USERNAME}
    Password: ${REGISTRY-SERVICE-ACCOUNT-PASSWORD}
    Login Succeeded!

2. Pull all the Nuage container images using following commands.

::

    $ docker pull registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-heat-api-5.4.1U1
    $ docker pull registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-heat-api-cfn-5.4.1U1
    $ docker pull registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-heat-engine-5.4.1U1
    $ docker pull registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-horizon-5.4.1U1
    $ docker pull registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-neutron-server-5.4.1U1

3. Re-tag the Nuage docker images to push them to local registry running on Undercloud.

::
    Note: In my case Undercloud IP is 192.168.24.1 and registry port is 8787
    $ docker tag registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-heat-api-5.4.1U1:latest 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-api-5.4.1U1:latest
    $ docker tag registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-heat-api-cfn-5.4.1U1:latest 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-api-cfn-5.4.1U1:latest
    $ docker tag registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-heat-engine-5.4.1U1:latest 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-engine-5.4.1U1:latest
    $ docker tag registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-horizon-5.4.1U1:latest 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-horizon-5.4.1U1:latest
    $ docker tag registry.connect.redhat.com/nuagenetworks/rhosp14-openstack-neutron-server-5.4.1U1:latest 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-neutron-server-5.4.1U1:latest


4. Push the Nuage container images to the local registry.

::

    docker push 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-api-5.4.1U1:latest
    docker push 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-api-cfn-5.4.1U1:latest
    docker push 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-engine-5.4.1U1:latest
    docker push 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-horizon-5.4.1U1:latest
    docker push 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-neutron-server-5.4.1U1:latest


5. Create /home/stack/templates/overcloud_images.yaml file and below to point Heat, Horizon, Neutron, and their Docker configuration images to ones in the local registry:

::

    parameter_defaults:
      DockerHeatApiCfnConfigImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-api-cfn-5.4.1U1:latest
      DockerHeatApiCfnImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-api-cfn-5.4.1U1:latest
      DockerHeatApiConfigImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-api-5.4.1U1:latest
      DockerHeatApiImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-api-5.4.1U1:latest
      DockerHeatConfigImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-api-5.4.1U1:latest
      DockerHeatEngineImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-heat-engine-5.4.1U1:latest
      DockerHorizonConfigImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-horizon-5.4.1U1:latest
      DockerHorizonImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-horizon-5.4.1U1:latest
      DockerInsecureRegistryAddress:
      - 192.168.24.1:8787
      DockerNeutronApiImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-neutron-server-5.4.1U1:latest
      DockerNeutronConfigImage: 192.168.24.1:8787/nuagenetworks/rhosp14-openstack-neutron-server-5.4.1U1:latest


Phase 8: Deploy the Overcloud.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use the Heat templates with the the command-line based template to deploy the Overcloud.

Use the ``openstack overcloud deploy`` command options to pass the environment files and to create or update an Overcloud deployment where:

    * neutron-nuage-config.yaml has the Nuage-specific Controller parameter values.
    * node-info.yaml has information specifying the count and flavor for the Controller and Compute nodes.
    * nova-nuage-config.yaml has the Nuage-specific Compute parameter values.


1. For a non-HA Overcloud deployment, use one of the following commands:

::

    openstack overcloud deploy --templates -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server
    
    For a virtual deployment, add the --libvirt-type parameter:
    openstack overcloud deploy --templates --libvirt-type qemu -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server


2. For an HA deployment, use one of the following commands:

::

    openstack overcloud deploy --templates -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server
    
    For a virtual deployment, add the --libvirt-type parameter:
    openstack overcloud deploy --templates --libvirt-type qemu -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server

3. For a Linux-bonding HA deployment with Nuage, use the following:

::
    openstack overcloud deploy --templates -e /home/stack/templates/overcloud_images.yaml -e /home/stack/templates/node-info.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/network-environment.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/network-isolation.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/net-bond-with-vlans.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server


where:
   * ``neutron-nuage-config.yaml`` is Controller specific parameter values.
   * ``nova-nuage-config.yaml`` is Compute specific parameter values.
   * ``node-info.yaml`` is Information specifies count and flavor for Controller and Compute nodes.
   * ``overcloud_images.yaml`` is Nuage containers for Overcloud heat, Horizon and Neutron.
   * ``network-environment.yaml`` Configures additional network environment variables
   * ``network-isolation.yaml`` Enables creation of networks for isolated overcloud traffic
   * ``net-bond-with-vlans.yaml`` Configures an IP address and a pair of bonded nics on each network



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


3. Verify that the containers are running.


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
        ovs_version: "5.4.1-11-nuage"


Parameters in the Heat Templates
---------------------------------

This section has the details about the parameters specified in the template files. It also describes the configuration files where the parameters are set and used.

Go to http://docs.openstack.org/developer/heat/template_guide/hot_guide.html and https://docs.openstack.org/rocky/configuration/ for more information.


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
      NeutronNuageNetPartitionName: 'Nuage_Partition_14'
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
      #
      # NOTE: (Since Rocky)
      # ControlPlaneSubnetCidr: It is no longer a requirement to provide the
      #                         parameter. The attribute is resolved from the
      #                         ctlplane subnet(s).
      # ControlPlaneDefaultRoute: It is no longer a requirement to provide this
      #                           parameter. The attribute is resolved from the
      #                           ctlplane subnet(s).
      # EC2MetadataIp: It is no longer a requirement to provide this parameter. The
      #                attribute is resolved from the ctlplane subnet(s).
      #
    {% for network in networks if network.enabled|default(true) %}
      # Customize the IP subnet to match the local environment
    {%-     if network.ipv6|default(false) %}
      {{network.name}}NetCidr: '{{network.ipv6_subnet}}'
    {%-     else %}
      {{network.name}}NetCidr: '{{network.ip_subnet}}'
    {%-     endif %}
      # Customize the IP range to use for static IPs and VIPs
    {%-     if network.name == 'External' %}
      # Leave room if the external network is also used for floating IPs
    {%-     endif %}
    {%-     if network.ipv6|default(false) %}
      {{network.name}}AllocationPools: {{network.ipv6_allocation_pools}}
    {%-     else %}
      {{network.name}}AllocationPools: {{network.allocation_pools}}
    {%-     endif %}
    {%-     if network.ipv6|default(false) and network.gateway_ipv6|default(false) %}
      # Gateway router for routable networks
      {{network.name}}InterfaceDefaultRoute: '{{network.gateway_ipv6}}'
    {%-     elif network.gateway_ip|default(false) %}
      # Gateway router for routable networks
      {{network.name}}InterfaceDefaultRoute: '{{network.gateway_ip}}'
    {%-     endif %}
    {%-     if network.vlan is defined %}
      # Customize the VLAN ID to match the local environment
      {{network.name}}NetworkVlanID: {{network.vlan}}
    {%-     endif %}
    {%-     if network.enabled|default(true) and network.routes %}
      # Routes to add to host_routes property of the subnets in neutron.
      {{network.name}}Routes: {{network.routes|default([])}}
    {%-     endif %}
    {% endfor %}
    {#- FIXME: These global parameters should be defined in a YAML file, e.g. network_data.yaml. #}
      # Define the DNS servers (maximum 2) for the overcloud nodes
      # When the list is no set or empty, the nameservers on the ctlplane subnets will be used.
      # (ctlplane subnets nameservers are controlled by the ``undercloud_nameservers`` option in ``undercloud.conf``)
      DnsServers: ['135.1.1.111']
      # List of Neutron network types for tenant networks (will be used in order)
      NeutronNetworkType: 'vxlan,vlan'
      # The tunnel type for the tenant network (vxlan or gre). Set to '' to disable tunneling.
      NeutronTunnelTypes: 'vxlan'
      # Neutron VLAN ranges per network, for example 'datacentre:1:499,tenant:500:1000':
      NeutronNetworkVLANRanges: 'datacentre:1:1000'
      # Customize bonding options, e.g. "mode=4 lacp_rate=1 updelay=1000 miimon=100"
      # for Linux bonds w/LACP, or "bond_mode=active-backup" for OVS active/backup.
      BondInterfaceOvsOptions: "bond_mode=active-backup"


node-info.yaml for Non-HA Deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Compute and Controller count can be set here

    parameter_defaults:
      ControllerCount: 1
      ComputeCount: 1


node-info.yaml for HA Deployments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Compute and Controller count can be set here

    parameter_defaults:
      ControllerCount: 3
      ComputeCount: 1


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

