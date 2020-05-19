.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

========================================================================
Integrating Nuage VSP 20.0.x with Red Hat OpenStack Platform Director 16
========================================================================

This document has the following topics:

.. contents::
   :local:
   :depth: 3

This document describes how the Nuage VSP integrates with Red Hat OpenStack Platform Director (OSPD).
The Nuage OpenStack plugins allow users to deploy flexible network configurations, including routers, subnets, and security groups along with other Nuage OpenStack extensions such as VSD-managed routers and subnets, which are shared between OpenStack and other cloud management systems.
For more information about the Nuage OpenStack ML2 driver, see the "Nuage Neutron ML2 Driver Guide."

This document has information about the requirements and recommended network topologies to deploy Red Hat OSP Director with Nuage VSP.
It describes the deployment workflow that includes downloading the required packages, setting up the Undercloud and Overcloud, and creating and configuring environment files and Heat templates for the deployment. It also provides sample environment files that you can modify for your deployment.


Red Hat OpenStack Platform Director
-----------------------------------

The Red Hat OpenStack Platform Director (OSPD) is a toolset for installing and managing an OpenStack environment. It is based primarily on the OpenStack TripleO project. It uses an OpenStack deployment, referred to as the Undercloud, to deploy an OpenStack cluster, referred to as an Overcloud.

The OpenStack Platform Director is an image-based installer. It uses a single image (for example, overcloud-full.qcow2) that is deployed on the Controller and Compute nodes belonging to the OpenStack cluster (Overcloud). This image contains all the packages needed during the deployment. The deployment creates only the configuration files and databases required by the different services and starts the services in the correct order. During a deployment, no new software is installed.

For integration of OpenStack Platform Director with the Nuage VSP, use the command-line based deployment option.

OpenStack Platform Director uses Heat to orchestrate the deployment of an OpenStack environment. The actual deployment is done through Heat templates and Puppet. Users provide any custom input in templates using the ``openstack overcloud deploy`` command. When this command is run, all the templates are parsed to create the Hiera database, and then a set of Puppet manifests, also referred to as TripleO Heat templates, are run to complete the deployment. The Puppet code in turn uses the Puppet modules developed to deploy different services of OpenStack (such as puppet-nova, puppet-neutron, and puppet-cinder).

The OpenStack Platform Director architecture allows partners to create custom templates. Partners create new templates to expose parameters specific to their modules.  These templates can then be passed through the ``openstack overcloud deploy`` command during the deployment. Changes to the Puppet manifests are required to handle the new values in the Hiera database and to act on them to deploy the partner software.


Requirements and Best Practices
---------------------------------

For Nuage Networks Virtualized Services Platform (VSP) (Virtualized Services Directory [VSD] and Virtualized Services Controller [VSC]) requirements and best practices, see the *VSP User Guide* for the deployment requirements. Before deploying OpenStack, the VSP components (VSD and VSC) should already be deployed.

For Red Hat OpenStack Platform Director 16.0 requirements and best practices, see the Red Hat upstream documentation:
https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/director_installation_and_usage/


Recommended Topologies
-----------------------

The deployment topology and networking segmentation varies depending on the OpenStack end-to-end requirements and underlay topology. A typical OpenStack setup with Nuage integration has the following topology:

.. figure:: ./sw1024.png

Workflow Overview of the Nuage VSP Integration with OpenStack Platform Director
--------------------------------------------------------------------------------

The workflow to integrate Nuage VSP with OpenStack Platform Director includes these phases:

.. figure:: ./sw1027.png

* **Phase 0: Install the VSP Core Components**

  Before installing OSPD on the Undercloud, install and configure VSD and VSC. See `Recommended Topologies`_ for a typical OpenStack setup with Nuage integration.

  Depending on your deployment, you may also install and configure WBX as a leaf/spine switch for Data Center and Enterprise networks deployments. See the WBX documentation for more details.

* **Phase 1: Install Red Hat OpenStack Platform Director**

  In this phase, you install Director on the Undercloud system by following the process in the Red Hat documentation.

* **Phase 2: Download Nuage Source Code**

  In this phase,  you get the following files on Director for the Nuage Overcloud deployment:

  - Nuage Tripleo Heat templates
  - Image patching files
  - Additional scripts

* **Phase 3: Prepare Nuage Repository and Containers**

  In this phase, you prepare Nuage Repository and Containers for the integration.

  - **Phase 3.1: Download the Nuage VSP RPMs and Create a Yum Repository**

    In this phase, you download the Nuage RPMs and create a repository for them.

    **Phase 3.2: Prepare Nuage Containers**

    In this phase, you prepare Nuage containers for the integration.

* **Phase 4: Prepare the Overcloud**

  In this phase, you follow procedures in this document and in the Red Hat documentation to do the basic configuration of the Overcloud.

  - **Phase 4.1: Register and Inspect the Bare Metal Nodes**

    Follow the procedures in the Red Hat documentation for registering and inspecting the hardware nodes in the "Configuring a Basic Overcloud using the CLI Tools" section and check the node status.

  - **Phase 4.2: Modify the Overcloud Image**

    To install the required Nuage packages, you run the script to patch the the Overcloud image.

    If you are using the *No Patching* process, skip this phase and follow the steps in the `Phase 4.3: No Patching Workflow`_

  - **Phase 4.3: No Patching Workflow**

    In this release, this feature is for Tech Preview only.

    In this phase, follow the steps in this document to automatically install all the required Nuage packages on the Overcloud without running the script to patch the image.

  - **Phase 4.4: Create the Dataplane Roles and Update the Node Profiles**

    In this phase, you add the Nuage Heat templates and dataplane roles for the Nuage integration.
    Roles define which actions users can perform. For more information about the supported roles, go to `Phase 4: Prepare the Overcloud`_

  - **Phase 4.5: Generate a CMS ID for the OpenStack Deployment**

    The Cloud Management System (CMS) ID is created to identify a specific Compute or Controller node.

  - **Phase 4.6: Customize the Environment Files**

    In this phase, you modify the environment files for your deployment and assign roles (profiles) to the Compute and Controller nodes.
    The files are populated with the required parameters.
    Nuage provides Heat templates and environment files to configure Neutron on the Controller node and RPMs (such as nuage-openvswitch and nuage-metadata-agent) on Compute nodes.

* **Phase 5: Deploy Overcloud**

  In this phase, you use the ``openstack overcloud deploy`` command with different options to deploy the various use cases.


Deployment Workflow
---------------------

Phase 0: Install the VSP Core Components
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To install VSD and VSC, see the *VSP Install Guide* and the  *VSP User Guide* for the deployment requirements and procedures.

To install WBX, see the WBX documentation.

Phase 1: Install Red Hat OpenStack Platform Director
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To prepare for the Nuage VSP integration, install Director on the Undercloud system by following the steps in the Red Hat documentation:

https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/director_installation_and_usage/director_installation_and_configuration

Phase 2: Download Nuage Source Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this phase, get the Nuage Tripleo Heat Templates, image patching files, and the other scripts by using the following commands on the Undercloud:

::

    cd /home/stack
    git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b <release-tag>
    ln -s nuage-ospdirector/nuage-tripleo-heat-templates .

    Example:

    cd /home/stack
    git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b 16.200x.1
    ln -s nuage-ospdirector/nuage-tripleo-heat-templates .



Phase 3: Prepare Nuage Repository and Containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Phase 3.1: Download the Nuage VSP RPMs and Create a Yum Repository
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

For Nuage VSP integrations, download all the required components and create a yum repository reachable from the Undercloud hypervisor or any other machine used to modify the Overcloud image (see `Phase 4.2: Modify the Overcloud Image`_).

The repository contents may change depending on the roles configured for your deployment.

::

   +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
   | Group          | Packages                                     | Location (tar.gz or link)                                                                 |
   +================+==============================================+===========================================================================================+
   |                | nuage-bgp                                    | nuage-vrs-el8                                                                             |
   |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
   | Nuage          | nuage-openstack-neutronclient                | nuage-openstack                                                                           |
   | Common         +----------------------------------------------+-------------------------------------------------------------------------------------------+
   | Packages       | nuage-puppet-modules-6.2.0                   | https://github.com/nuagenetworks/nuage-ospdirector/tree/OSPD16/nuage-puppet-modules       |
   |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
   |                | nuage-metadata-agent                         | nuage-vrs-el8                                                                             |
   |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
   |                | python-openswitch-nuage                      | nuage-vrs-el8                                                                             |
   |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
   |                | nuage-openstack-neutron                      | nuage-openstack                                                                           |
   |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
   |                | nuage-openstack-horizon                      | nuage-openstack                                                                           |
   |                +----------------------------------------------+-------------------------------------------------------------------------------------------+
   |                | nuage-openstack-heat                         | nuage-openstack                                                                           |
   +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
   | Nuage VRS      | nuage-openvswitch                            | nuage-vrs-el8                                                                             |
   | Packages       +----------------------------------------------+-------------------------------------------------------------------------------------------+
   |                | selinux-policy-nuage                         | nuage-selinux                                                                             |
   +----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+
   | Nuage SR-IOV   | nuage-topology-collector (for Nuage SR-IOV)  | nuage-openstack                                                                           |
   | packages       |                                              |                                                                                           |
   |----------------+----------------------------------------------+-------------------------------------------------------------------------------------------+


Phase 3.2: Prepare Nuage Containers
+++++++++++++++++++++++++++++++++++

In this phase, you prepare Nuage containers for the integration.


1. Add the below contents to /home/stack/containers-prepare-parameter.yaml. A complete file can be found in `Sample Environment Files`_.


::

        excludes:
        - horizon
        - heat-engine
        - heat-api-cfn
        - neutron-server
        - heat-api

      - push_destination: true
        includes:
        - horizon
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/horizon

      - push_destination: true
        includes:
        - neutron-server
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/neutron-server

      - push_destination: true
        includes:
        - heat-engine
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/heat-engine

      - push_destination: true
        includes:
        - heat-api-cfn
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/heat-api-cfn

      - push_destination: true
        includes:
        - heat-api
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/heat-api


2. Under `/home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/` you can find different openstack project folder. Please fill in nuage.repo in each folder with proper information.

::

    Sample nuage.repo
    [Nuage]
    name=nuage
    baseurl=http://url_to_nuage_repo
    enabled=1
    gpgcheck=1
    gpgkey=file:///tmp/RPM-GPG-KEY-Nuage


3. Copy Nuage Gpgkey to all these folder with name RPM-GPG-KEY-Nuage



Phase 4: Prepare the Overcloud
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this phase, you perform the basic configuration of the Overcloud.

The process includes modifying the Overload image and environment file, creating the dataplane roles and updating node profiles, and assigning the roles to a Compute or Controller node.

**Role**: A role is a personality assigned to a node where a specific set of operations is allowed.
For more information about roles, see the Red Hat OpenStack documentation:

   * https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/director_installation_and_usage/planning-your-overcloud

   * https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/advanced_overcloud_customization/chap-roles#sect-Creating_a_Custom_Roles_File

You only need to configure the roles for your deployment and assign the roles to the appropriate nodes. For example, the network topology diagram in `Workflow Overview of the Nuage VSP Integration with OpenStack Platform Director`_ shows that each Compute node has different roles:

   * Compute node with VRS only
   * Compute node with VRS and SR-IOV


Phase 4.1: Register and Inspect the Bare Metal Nodes
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

In the Red Hat OpenStack Platform Director documentation, follow the steps using the CLI *up to where* the ``openstack overcloud deploy`` command is run:

https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/director_installation_and_usage/creating-a-basic-overcloud-with-cli-tools

To verify the Ironic node status, follow these steps:

1. Check the bare metal node status.

   The results should show the *Provisioning State* status as *available* and the *Maintenance* status as *False*.

::

    openstack baremetal node list


2. If profiles are being set for a specific placement in the deployment, check the Overcloud profile status.

   The results should show the *Provisioning State* status as *available* and the *Current Profile* status as *control* or *compute*.

::

    openstack overcloud profiles list


Phase 4.2: Modify the Overcloud Image
++++++++++++++++++++++++++++++++++++++++

In this phase, you modify the overcloud-full.qcow2 image with the required Nuage packages.

When using the *No Patching* feature, skip this phase and follow the instructions in `Phase 4.3: No Patching Workflow`_

Follow these steps to modify the the Overcloud qcow image (overcloud-full.qcow2):


.. Note:: Please use rhel8 machine for image patching and do not run this on Undercloud Director (https://bugs.launchpad.net/tripleo/+bug/1823226)


1. Install the required packages: libguestfs-tools and python-yaml

::

    yum install libguestfs-tools python-yaml -y


2. Copy the *image-patching* folder from /home/stack/nuage-ospdirector/image-patching/ on the hypervisor machine that is accessible to the nuage-rpms repository.

::

    cd nuage_image_patching_scripts


3. Copy *overcloud-full.qcow2* from /home/stack/images/ on the Undercloud director to this location and make a backup of *overcloud-full.qcow2*.

::

    cp overcloud-full.qcow2 overcloud-full-bk.qcow2

4. This script takes in *nuage_patching_config.yaml* as input parameters. You need to configure the following parameters:

   * ImageName (required) is the name of the qcow2 image (for example, overcloud-full.qcow2).
   * DeploymentType (required) is for type of deployment specifed by the user. Select *vrs*.

     - For any combination of VRS and SR-IOV deployments, specify the deployment type as ["vrs"].

   * RhelUserName (optional) is the user name for the Red Hat Enterprise Linux (RHEL) subscription.
   * RhelPassword (optional) is the password for the Red Hat Enterprise Linux subscription.
   * RhelPool (optional) is the Red Hat Enterprise Linux pool to which the base packages are subscribed.
   * RhelSatUrl (optional) is the URL for the Red Hat Satellite server.
   * RhelSatOrg (optional) is the organization for the Red Hat Satellite server.
   * RhelSatActKey (optional) is the activation key for the Red Hat Satellite server.

     .. Note:: If Nuage packages are available using the activation key parameter, *RepoFile* becomes optional.

   * RpmPublicKey (optional) is where you pass all the file paths of the GPG key that you want to add to your Overcloud images before deploying the required packages for your deployment.

     .. Note::

        * Any Nuage package signing keys are delivered with other Nuage artifacts.  See ``nuage-package-signing-keys-*.tar.gz``.

        * Make sure to copy the GPGKey files to the same folder as the ``nuage_overcloud_full_patch.py`` patching script directory.

   * RepoFile (usually required but optional for Red Hat Satellite) is the name of the repository hosting the RPMs required for patching.

     - Make sure to place the repository file in the same folder as the ``nuage_overcloud_full_patch.py`` patching script directory.
     - If Nuage packages are available using the activation key of a Red Hat Satellite server, *RepoFile* becomes optional.
     - RepoFile can contain only a single Nuage repository with the required Nuage packages and can also have extra repositories with non-Nuage packages.

   * logFileName is used to pass log filename.

   For examples of nuage.repo and nuage_patching_config.yaml, go to `Nuage Patching Configuration`_.

5. Run the following command that provides the parameter values to start the image patching workflow:

::

    python3 nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml


.. Note:: If the image patching fails, remove the partially patched overcloud-full.qcow2 and create a copy of it from the backup image before retrying the image patching workflow.

    ::

        rm overcloud-full.qcow2
        cp overcloud-full-bk.qcow2 overcloud-full.qcow2


6. Verify that the *machine-id* is clear in the Overcloud image. The result should be empty output.

::

    guestfish -a overcloud-full.qcow2 run : mount /dev/sda / : cat /etc/machine-id

7. Copy the patched image back to /home/stack/images/ on the Undercloud and upload it to Glance.

   a. Check that the current images are uploaded:

        ::

            [stack@director ~]$ source ~/stackrc
            (undercloud) [stack@director ~]$ openstack image list

   b. If the ``openstack image list`` command returns null, run the following command to upload all images in /home/stack/images/ to Glance.

        ::

            [stack@director images]$ openstack overcloud image upload --image-path /home/stack/images/

   c. If the ``openstack image list`` command returns the output similar to this:

        ::

            +--------------------------------------+---------------------------------+--------+
            | ID                                   | Name                            | Status |
            +--------------------------------------+---------------------------------+--------+
            | 90cec28e-9609-4d2e-b87b-030804a99090 | overcloud-full                  | active |
            | 4c3dad99-1463-4391-9663-9b8074f714f1 | overcloud-full-initrd           | active |
            | 66e3ba1e-d080-4199-8ad6-2e54439c8d11 | overcloud-full-vmlinuz          | active |
            +--------------------------------------+---------------------------------+--------+


      Run the following commands to update the images to Glance:

        ::

            (undercloud) [stack@director images]$ openstack overcloud image upload --update-existing --image-path /home/stack/images/
            (undercloud) [stack@director images]$ openstack overcloud node configure $(openstack baremetal node list -c UUID -f value)


Phase 4.3: No Patching Workflow
++++++++++++++++++++++++++++++++

In this release, this feature is for Tech Preview only.

The *No Patching* feature installs all the required Nuage packages on Overcloud nodes during the Overcloud deployment, instead of patching the Overcloud image.

Follow these instructions:

1. Make sure that the following servers are available:

    a. Red Hat Satellite Server with an activation_key that has both the Red Hat and Nuage repositories enabled by default.
    b. HTTP(S) server hosting the required Nuage GPGKeys.

2. Set NuageGpgKeys to the location where Nuage GPGKeys are hosted inside nuage-tripleo-heat-temaplates/environment/nova-nuage-config.yaml

   For example, if you have Nuage GPGKeys Nuage-RPM-GPG-Key1 Nuage-RPM-GPG-Key2 hosted in the 1.2.3.4 HTTP server, set NuageGpgKeys as follows:

   ::

        NuageGpgKeys: ['http://1.2.3.4/Nuage-RPM-GPG-Key1', 'http://1.2.3.4/Nuage-RPM-GPG-Key2']


3. Follow the instructions in the  Red Hat documentation for `Registering to Red Hat Satellite Server <https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/advanced_overcloud_customization/ansible-based-registration#registering-the-overcloud-to-red-hat-satellite>`_


Phase 4.4: Create the Dataplane Roles and Update the Node Profiles
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In this phase, you add the Nuage Heat templates and dataplane roles for the Nuage integration.

1. Create a *nuage_roles_data.yaml* file with all the required roles for the current Overcloud deployment.

   This example shows how to create *nuage_roles_data.yaml* with a Controller and Compute nodes for VRS and SR-IOV. The respective roles are specified in the same order. The following example has the respective role names mentioned in the same order.

::

    Syntax:
    openstack overcloud roles generate -o /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml Controller Compute <role> <role> ...

    Example:
    openstack overcloud roles generate -o /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml Controller Compute ComputeSriov


.. Note:: It is not mandatory to create nuage_roles_data.yaml with all the roles shown in the example. You can specify only the required ones for your deployment.

2. Create ``node-info.yaml`` in /home/stack/templates/ and specify the roles and number of nodes.

  This example shows how to create a *node-info.yaml* file for deployment with three Controller, two Compute, two ComputeSriov roles:

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
      OvercloudComputeSriovFlavor: computesriov
      ComputeSriovCount: 2

.. Note:: It is not mandatory to provide node info for all the roles shown in the example. You can specify the node information only for the required roles.


Phase 4.5: Generate a CMS ID for the OpenStack Deployment
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The Cloud Management System (CMS) ID is used to identify a specific Compute or Controller node.

In this phase, you generate the CMS ID used to configure your OpenStack deployment with the VSD deployment.

1. Go to `Generate CMS ID <../../nuage-tripleo-heat-templates/scripts/generate-cms-id>`_ for the files and script to generate the CMS ID, and follow the instructions in the README.md file.

   The CMS ID is displayed in the output, and a copy of it is stored in a file called cms_id.txt in the same folder.

2. Add the CMS ID to the /home/stack/nuage-tripleo-heat-templates/environments/neutron-nuage-config.yaml template file for the ``NeutronNuageCMSId`` parameter.


Phase 4.6: Customize the Environment Files
+++++++++++++++++++++++++++++++++++++++++++

In this phase, you create and customize environment files and tag nodes for specific profiles. These profile tags match your nodes to flavors, which assign the flavors to deployment roles.

For more information about the parameters in the environment files, go to `Parameters in Environment Files`_.

For sample environment files, go to `Sample Environment Files`_.

1. Go to `/home/stack/nuage-tripleo-heat-templates/environments/` on the Undercloud machine.

2. Customize these environment files, and add required values, such as CMS ID, and other parameters.

    * neutron-nuage-config.yaml - Add the generated ``cms_id`` to the ``NeutronNuageCMSId`` parameter.
    * nova-nuage-config.yaml

   Go to `Parameters in Environment Files`_ for details about the required parameters.


3. Assign roles to the Compute and Controller nodes, as described in the following steps.

   This is the mapping of the Nuage OpenvSwitch packages to role names:

::

   +----------------+----------------------------------------------------+
   | Dataplane      | Role Name                                          |
   +================+====================================================+
   | VRS            | Compute                                            |
   |----------------+----------------------------------------------------+
   | SR-IOV         | ComputeSriov                                       |
   +----------------+----------------------------------------------------+


Nuage Controller Role (Controller)
''''''''''''''''''''''''''''''''''''

      For a Controller node, assign the Controller role to each of the Controller nodes:

::

   openstack baremetal node set --property capabilities='profile:control,boot_option:local' <node-uuid>

VRS Compute Role (Compute)
'''''''''''''''''''''''''''

    For a VRS Compute node, assign the appropriate profile:

::

    openstack baremetal node set --property capabilities='profile:compute,boot_option:local' <node-uuid>

SR-IOV Role (ComputeSriov)
'''''''''''''''''''''''''''

Nuage supports the Virtual Routing and Switching (VRS) role (Compute) and the Single Root I/O Virtualization (SR-IOV) role (ComputeSriov).
The Nuage plugin supports Single Root I/O Virtualization (SR-IOV)-attached VMs (https://wiki.openstack.org/wiki/SR-IOV-Passthrough-For-Networking) with VSP-managed VMs on the same KVM hypervisor cluster.
For more information, go to the "VSP OpenStack ML2 Driver Guide*.

    To enable SR-IOV, perform the following steps:

    1. Create a flavor and profile for ComputeSriov:

       Refer to https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/director_installation_and_usage/creating-a-basic-overcloud-with-cli-tools

    ::

        openstack flavor create --id auto --ram 4096 --disk 40 --vcpus 1 computesriov
        openstack flavor set --property "cpu_arch"="x86_64" --property "capabilities:boot_option"="local" --property "capabilities:profile"="computesriov" --property resources:CUSTOM_BAREMETAL='1' --property resources:DISK_GB='0' --property resources:MEMORY_MB='0' --property resources:VCPU='0' computesriov


    2. Assign SR-IOV nodes with the appropriate ComputeSriov profile:

    ::

        openstack baremetal node set --property capabilities='profile:computesriov,boot_option:local' <node-uuid>


    3. To deploy the Overcloud, additional parameters and template files are required.

       * Include the following parameter values in the Heat template *neutron-nuage-config.yaml*:

         ::

             NeutronServicePlugins: 'NuagePortAttributes,NuageAPI,NuageL3,trunk,NuageNetTopology'
             NeutronTypeDrivers: "vlan,vxlan,flat"
             NeutronMechanismDrivers: ['nuage','nuage_sriov','sriovnicswitch']
             NeutronFlatNetworks: '*'
             NeutronTunnelIdRanges: "1:1000"
             NeutronNetworkVLANRanges: "physnet1:2:100,physnet2:2:100"
             NeutronVniRanges: "1001:2000"


       * Include  the *neutron-sriov.yaml* file in the Overcloud deployment command. For an example, go to `Sample Environment Files`_.

         For more information, refer to the `CONFIGURING SR-IOV <https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/network_functions_virtualization_planning_and_configuration_guide/part-sriov-nfv-configuration#sect-configuring-sriov>`_ section from Red Hat.

       .. Note:: Make sure that the physical network mappings parameters in neutron-nuage-config.yaml and neutron-sriov.yaml match with your hardware profile. To check interface information for your inspected nodes, run ``openstack baremetal introspection interface list [node uuid]``.

Network Isolation
''''''''''''''''''

   The Nuage plugin supports Network Isolation on the Overcloud nodes. It provides fully distributed L2 and L3 networking, including L2 and L3 network isolation, without requiring centralized routing instances such as the Neutron L3 agent.

   **Linux Bonding with VLANs**

    The plugin uses the default Linux bridge and Linux bonding. Go to https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.0/html/advanced_overcloud_customization/overcloud-network-interface-bonding for more information about Linux bonding on OpenStack.

    To deploy the Overcloud Controller and ComputeSriov, Nuage provides `bond-with-vlans network templates <../../nuage-tripleo-heat-templates/network/config/bond-with-vlans/>`_ that configure the Linux bonding with VLANs.

    By default, these network templates support the following topology. You can modify the templates to match your topology.

    * controller.yaml expects the Controller nodes to have three interfaces, where the first interface is for provisioning and the rest are for Linux bonding with VLANs for all networks.
    * compute.yaml expects Compute nodes to have three interfaces, where the first interface is for provisioning and the rest are for Linux bonding with VLANs for all networks
    * computesriov.yaml expects the ComputeSriov nodes to have five interfaces. The first interface is for provisioning. The second and third interfaces are for Linux bonding with VLANs for all networks except the Tenant network. The rest are for creating VF's for SR-IOV to configure Linux bonding with VLANs for the Tenant network.

    The following example shows the changes to the sample network template for the Linux bonding with VLANs for all interface types.

    To customize the template, modify ``/home/stack/nuage-tripleo-heat-templates/environments/network-environment.yaml`` with the appropriate values.

     ::

                ...
                  - type: linux_bond
                    name: bond1
                    mtu:
                      get_attr: [MinViableMtu, value]
                    bonding_options:
                      get_param: BondInterfaceOvsOptions
                    use_dhcp: false
                    dns_servers:
                      get_param: DnsServers
                    members:
                    - type: interface
                      name: nic2
                      mtu:
                        get_attr: [MinViableMtu, value]
                      primary: true
                    - type: interface
                      name: nic3
                      mtu:
                        get_attr: [MinViableMtu, value]
                  - type: vlan
                    device: bond1
                    mtu:
                      get_param: StorageMtu
                    vlan_id:
                      get_param: StorageNetworkVlanID
                    addresses:
                    - ip_netmask:
                        get_param: StorageIpSubnet
                    routes:
                      list_concat_unique:
                        - get_param: StorageInterfaceRoutes
                  - type: vlan
                    device: bond1
                    mtu:
                      get_param: StorageMgmtMtu
                    vlan_id:
                      get_param: StorageMgmtNetworkVlanID
                    addresses:
                    - ip_netmask:
                        get_param: StorageMgmtIpSubnet
                    routes:
                      list_concat_unique:
                        - get_param: StorageMgmtInterfaceRoutes
                  - type: vlan
                    device: bond1
                    mtu:
                      get_param: InternalApiMtu
                    vlan_id:
                      get_param: InternalApiNetworkVlanID
                    addresses:
                    - ip_netmask:
                        get_param: InternalApiIpSubnet
                    routes:
                      list_concat_unique:
                        - get_param: InternalApiInterfaceRoutes
                  - type: vlan
                    device: bond1
                    mtu:
                      get_param: TenantMtu
                    vlan_id:
                      get_param: TenantNetworkVlanID
                    addresses:
                    - ip_netmask:
                        get_param: TenantIpSubnet
                    routes:
                      list_concat_unique:
                        - get_param: TenantInterfaceRoutes
                  - type: vlan
                    device: bond1
                    mtu:
                      get_param: ExternalMtu
                    vlan_id:
                      get_param: ExternalNetworkVlanID
                    addresses:
                    - ip_netmask:
                        get_param: ExternalIpSubnet
                    routes:
                      list_concat_unique:
                        - get_param: ExternalInterfaceRoutes
                        - - default: true
                            next_hop:
                              get_param: ExternalInterfaceDefaultRoute
                ...


    .. Note::

       In OSPD 9 and later, a verification step was added where the Overcloud nodes ping the gateway to verify connectivity on the external network VLAN. Without this verification step, the deployment, such as one with Linux bonding and Network Isolation, would fail.

       For this verification step, the *ExternalInterfaceDefaultRoute* IP configured in the network-environment.yaml template should be reachable from the Overcloud Controller nodes on the external API VLAN. This gateway can also be on the Undercloud. The gateway needs to be tagged with the same VLAN ID as that for the external API network of the Controller. The *ExternalInterfaceDefaultRoute* IP should be able to reach outside because the Overcloud Controller uses this IP address as a default route to reach the Red Hat Registry to pull the Overcloud container images.


Phase 5: Deploy the Overcloud
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``openstack overcloud deploy`` command options to pass the environment files and to create or update an Overcloud deployment where:

    * neutron-nuage-config.yaml has the Nuage-specific Controller parameter values.
    * node-info.yaml has information specifying the count and flavor for the Controller and Compute nodes.
    * nova-nuage-config.yaml has the Nuage-specific Compute parameter values.

For SR-IOV, also include the following role and environment files.

        * nuage_roles_data.yaml
        * neutron-sriov.yaml


1. For VRS Overcloud deployment, use one of the following commands:

::

    For VRS Computes as bare metal, use:
    openstack overcloud deploy --templates -r /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml -e /home/stack/containers-prepare-parameter.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/nuage-tripleo-heat-templates/nuage-overcloud-resource-registry.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server --timeout timeout

    For VRS Computes as virtual machines, add the --libvirt-type parameter:
    openstack overcloud deploy --templates --libvirt-type qemu -r /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml -e /home/stack/containers-prepare-parameter.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/nuage-tripleo-heat-templates/nuage-overcloud-resource-registry.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server --timeout timeout


2. For SR-IOV, use following command:

::

   openstack overcloud deploy --templates -r /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml -e /home/stack/containers-prepare-parameter.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/nuage-tripleo-heat-templates/nuage-overcloud-resource-registry.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/nova-nuage-config.yaml -e /home/stack/templates/neutron-sriov.yaml --ntp-server ntp-server --timeout timeout


3. For VRS Linux-bonding HA deployment with Nuage, use the following:

::

    openstack overcloud deploy --templates -r /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml -e /home/stack/containers-prepare-parameter.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/nuage-tripleo-heat-templates/nuage-overcloud-resource-registry.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/network-isolation.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/network-environment.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/net-bond-with-vlans.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/nova-nuage-config.yaml --ntp-server ntp-server --timeout timeout


4. For VRS, SR-IOV deployment with Nuage using Linux-bonding, use the following:

::

    openstack overcloud deploy --templates -r /home/stack/nuage-tripleo-heat-templates/templates/nuage_roles_data.yaml -e /home/stack/containers-prepare-parameter.yaml -e /home/stack/templates/node-info.yaml -e /home/stack/nuage-tripleo-heat-templates/nuage-overcloud-resource-registry.yaml -e /usr/share/openstack-tripleo-heat-templates/environments/network-isolation.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/network-environment.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/net-bond-with-vlans.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/neutron-nuage-config.yaml -e /home/stack/nuage-tripleo-heat-templates/environments/nova-nuage-config.yaml -e /home/stack/templates/neutron-sriov.yaml --ntp-server ntp-server --timeout timeout


where:

   * ``nuage_roles_data.yaml`` has the roles required for overcloud deployment.
   * ``nuage-overcloud-resource-registry.yaml`` has the services mapping to respective deployment heat template
   * ``node-info.yaml`` has information about the count and flavor for Controller and Compute nodes.
   * ``neutron-nuage-config.yaml`` has Controller-specific parameter values.
   * ``nova-nuage-config.yaml`` has Compute-specific parameter values.
   * ``neutron-sriov.yaml`` has the Neutron SR-IOV-specific parameter values.
   * ``network-environment.yaml`` configures additional network environment variables.
   * ``network-isolation.yaml`` enables the creation of networks for isolated Overcloud traffic.
   * ``net-bond-with-vlans.yaml`` configures an IP address and a pair of bonded NICs on each network.
   * ``ntp-server`` has the NTP settings for the Overcloud nodes.


Phase 6: Verify that OpenStack Platform Director Has Been Deployed Successfully
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Run ``openstack stack list`` to verify that the stack was created.

::

    [stack@director ~]$ openstack stack list

    +--------------------------------------+------------+----------------------------------+-----------------+----------------------+-----------------+
    | ID                                   | Stack Name | Project                          | Stack Status    | Creation Time        | Updated Time    |
    +--------------------------------------+------------+----------------------------------+-----------------+----------------------+-----------------+
    | 75810b99-c372-463c-8684-f0d7b4e5743e | overcloud  | 1c60ab81cc924fe78355a76ee362386b | CREATE_COMPLETE | 2020-04-14T20:55:42Z | None            |
    +--------------------------------------+------------+----------------------------------+-----------------+----------------------+-----------------+


2. Run ``nova list`` to view the Overcloud Compute and Controller nodes.

::

    [stack@director ~]$ nova list
    +--------------------------------------+--------------------------+--------+------------+-------------+------------------------+
    | ID                                   | Name                     | Status | Task State | Power State | Networks               |
    +--------------------------------------+--------------------------+--------+------------+-------------+------------------------+
    | 3ca9a740-5f02-41f9-8596-4556964996f8 | overcloud-computesriov-0 | ACTIVE | -          | Running     | ctlplane=192.168.24.19 |
    | 1f220c11-6fc2-4ca8-a3f5-ed353f02ad89 | overcloud-controller-0   | ACTIVE | -          | Running     | ctlplane=192.168.24.13 |
    | b8982526-e308-4d6f-b370-38b6079f06e5 | overcloud-novacompute-0  | ACTIVE | -          | Running     | ctlplane=192.168.24.22 |
    +--------------------------------------+--------------------------+--------+------------+-------------+------------------------+


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
        ovs_version: "6.0.5-191-nuage"


Phase 7: Install the nuage-openstack-neutronclient RPM in the Undercloud (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The nuage-openstack-neutronclient RPM was downloaded and add to the repository with the other Nuage base packages in `Phase 3.1: Download the Nuage VSP RPMs and Create a Yum Repository`_

To complete the installation:

1. Enable the Nuage repository hosting the nuage-openstack-neutronclient on the Undercloud.

2. Run ``yum install -y nuage-openstack-neutronclient``

Phase 8: Manually Install and Run the Topology Collector for SR-IOV (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See the "Installation and Configuration: Topology Collection Agent and LLDP" section in the *Nuage VSP OpenStack Neutron ML2 Driver Guide*.

For more information, see the OpenStack SR-IOV documentation: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux_openstack_platform/7/html/networking_guide/sr-iov-support-for-virtual-networking


Nuage Patching Configuration
-----------------------------

For a local repository for Nuage OpenStack packages and Red Hat OpenStack-dependent packages:

1. This is an example of nuage_ospd16.repo:

::

    [nuage]
    name=nuage_osp16_nuage
    baseurl=http://1.2.3.4/nuage_osp16/nuage_repo
    enabled=1
    gpgcheck=1

    [extra]
    name=local_redhat_repo
    baseurl=http://1.2.3.4/extra_repo
    enabled=1
    gpgcheck=1

2. You can configure nuage_patching_config.yaml like this:

::

    ImageName: "overcloud-full.qcow2"
      # ["vrs"] --> vrs deployment
    DeploymentType: ["vrs"]
    RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
    RepoFile: './nuage_ospd16.repo'
    logFileName: "nuage_image_patching.log"


For a local repository for Nuage packages and a Red Hat Subscription for dependent packages:

1. This is an example of nuage_ospd16.repo:

::

    [nuage]
    name=nuage_osp16_nuage
    baseurl=http://1.2.3.4/nuage_osp16/nuage_repo
    enabled=1
    gpgcheck=1

2. You can configure nuage_patching_config.yaml like this:

::

    ImageName: "overcloud-full.qcow2"
      # ["vrs"] --> vrs deployment
    DeploymentType: ["vrs"]
    RhelUserName: 'abc'
    RhelPassword: '***'
    RhelPool: '1234567890123445'
    RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
    RepoFile: './nuage_ospd16.repo'
    logFileName: "nuage_image_patching.log"


For a Red Hat Satellite Server for Nuage packages and Red Hat-dependent packages:

1. Make sure the Red Hat Satellite activation key is configured with:

   - the Red Hat OpenStack Platform subscription enabled
   - A Nuage product containing the Nuage packages and the Nuage product subscription enabled

2. You can configure the nuage_patching_config.yaml like this:

::

    ImageName: "overcloud-full.qcow2"
      # ["vrs"] --> vrs deployment
    DeploymentType: ["vrs"]
    RhelSatUrl: 'https://satellite.example.com'
    RhelSatOrg: 'example_organization'
    RhelSatActKey: 'example_key'
    RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
    logFileName: "nuage_image_patching.log"


Parameters in Environment Files
---------------------------------

This section has the details about the parameters specified in the Heat template files. It also describes the configuration files where the parameters are set and used.

Go to http://docs.openstack.org/developer/heat/template_guide/hot_guide.html and https://docs.openstack.org/queens/configuration/ for more information.

For the Heat templates used by OpenStack Platform Director, go to http://git.openstack.org/cgit/openstack/tripleo-heat-templates

Parameters on the Neutron Controller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following parameters are mapped to values in the /etc/neutron/plugins/nuage/plugin.ini file on the Neutron Controller:

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


The following parameters are mapped to values in the /etc/neutron/neutron.conf file on the Neutron Controller:

.. Note:: The values for these parameters depend on the Nuage VSP configuration.

::

    NeutronServicePlugins
    Maps to service_plugins parameter in [DEFAULT] section


The following parameters are mapped to values in the /etc/nova/nova.conf file on the Neutron Controller:

.. Note:: These values for the parameters depend on the Nuage VSP configuration.

::

    UseForwardedFor
    Maps to use_forwarded_for parameter in [DEFAULT] section

    NeutronMetadataProxySharedSecret
    Maps to metadata_proxy_shared_secret parameter in [neutron] section


The following parameters are mapped to values in the /etc/neutron/plugins/ml2/ml2_conf.ini file on the Neutron Controller:

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


The following parameter is mapped to value in the /etc/heat/heat.conf file on the Controller:

::

    HeatEnginePluginDirs
    Maps to plugin_dirs in [DEFAULT] section


The following parameter is mapped to value in the /usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py on the Controller:

::

    HorizonCustomizationModule
    Maps to customization_module in HORIZON_CONFIG dict


The following parameter is mapped to value in the /etc/httpd/conf.d/10-horizon_vhost.conf on the Controller:

::

    HorizonVhostExtraParams
    Maps to CustomLog, Alias in this file


The following parameters are used to set and/or disable services in the Undercloud Puppet code:

::

    OS::TripleO::Services::NeutronDHCPAgent
    OS::TripleO::Services::NeutronL3Agent
    OS::TripleO::Services::NeutronMetadataAgent
    OS::TripleO::Services::NeutronOVSAgent
    OS::TripleO::Services::OVNDBs
    OS::TripleO::Services::OVNController
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

    NuageBridgeMTU
    Maps to BRIDGE_MTU parameter

    VrsExtraConfigs
    Used to configure extra parameters and values for nuage-openvswitch


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


Sample Environment Files
-------------------------

For the latest templates, go to the `Links to Nuage and OpenStack Resources`_ section.


containers-prepare-parameter.yaml
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    parameter_defaults:
      NtpServer: ['135.1.1.111']
      ContainerImageRegistryCredentials:
        registry.redhat.io:
          <user-name>: "<password>"
      ContainerImagePrepare:
      - push_destination: true
        set:
          ceph_alertmanager_image: ose-prometheus-alertmanager
          ceph_alertmanager_namespace: registry.redhat.io/openshift4
          ceph_alertmanager_tag: 4.1
          ceph_grafana_image: rhceph-3-dashboard-rhel7
          ceph_grafana_namespace: registry.redhat.io/rhceph
          ceph_grafana_tag: 3
          ceph_image: rhceph-4-rhel8
          ceph_namespace: registry.redhat.io/rhceph
          ceph_node_exporter_image: ose-prometheus-node-exporter
          ceph_node_exporter_namespace: registry.redhat.io/openshift4
          ceph_node_exporter_tag: v4.1
          ceph_prometheus_image: ose-prometheus
          ceph_prometheus_namespace: registry.redhat.io/openshift4
          ceph_prometheus_tag: 4.1
          ceph_tag: latest
          name_prefix: openstack-
          name_suffix: ''
          namespace: registry.redhat.io/rhosp-rhel8
          neutron_driver: ovn
          rhel_containers: false
          tag: '16.0'
        tag_from_label: '{version}-{release}'
        excludes:
        - horizon
        - heat-engine
        - heat-api-cfn
        - neutron-server
        - heat-api

      - push_destination: true
        includes:
        - horizon
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/horizon

      - push_destination: true
        includes:
        - neutron-server
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/neutron-server

      - push_destination: true
        includes:
        - heat-engine
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/heat-engine

      - push_destination: true
        includes:
        - heat-api-cfn
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/heat-api-cfn

      - push_destination: true
        includes:
        - heat-api
        modify_role: tripleo-modify-image
        modify_append_tag: "-nuage"
        modify_vars:
          tasks_from: modify_image.yml
          modify_dir_path: /home/stack/nuage-ospdirector/nuage-ospd16-dockerfiles/heat-api


nuage-overcloud-resource-registry.yaml
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    resource_registry:
      # Below services are disabled on Controller for neutron_driver: null
      OS::TripleO::Services::NeutronDhcpAgent: OS::Heat::None
      OS::TripleO::Services::NeutronL3Agent: OS::Heat::None
      OS::TripleO::Services::NeutronMetadataAgent: OS::Heat::None
      OS::TripleO::Services::NeutronOvsAgent: OS::Heat::None

      # Below services are disabled on Controller for neutron_driver: ovn
      OS::TripleO::Services::OVNDBs: OS::Heat::None
      OS::TripleO::Services::OVNController: OS::Heat::None

      # Override the NeutronMl2PluginBase to use Nuage inside Docker container
      OS::TripleO::Docker::NeutronMl2PluginBase: deployment/neutron/neutron-plugin-ml2-nuage.yaml
      OS::TripleO::Services::NeutronCorePlugin: deployment/neutron/neutron-plugin-ml2-nuage-container-puppet.yaml

      # Below services are disabled on Compute for Nuage OpenvSwitch
      OS::TripleO::Services::OVNMetadataAgent:  OS::Heat::None
      OS::TripleO::Services::ComputeNeutronOvsAgent: OS::Heat::None

      # Override the ComputeNeutronCorePlugin to use Nuage OpenvSwitch on compute nodes
      OS::TripleO::Services::ComputeNeutronCorePlugin: deployment/nova/nuage-compute-vrs.yaml


network-environment.yaml
~~~~~~~~~~~~~~~~~~~~~~~~

::

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

      # Customize the IP subnet to match the local environment
      StorageNetCidr: '172.16.1.0/24'
      # Customize the IP range to use for static IPs and VIPs
      StorageAllocationPools: [{'start': '172.16.1.4', 'end': '172.16.1.250'}]
      # Customize the VLAN ID to match the local environment
      StorageNetworkVlanID: 30


      # Customize the IP subnet to match the local environment
      StorageMgmtNetCidr: '172.16.3.0/24'
      # Customize the IP range to use for static IPs and VIPs
      StorageMgmtAllocationPools: [{'start': '172.16.3.4', 'end': '172.16.3.250'}]
      # Customize the VLAN ID to match the local environment
      StorageMgmtNetworkVlanID: 40


      # Customize the IP subnet to match the local environment
      InternalApiNetCidr: '172.16.2.0/24'
      # Customize the IP range to use for static IPs and VIPs
      InternalApiAllocationPools: [{'start': '172.16.2.4', 'end': '172.16.2.250'}]
      # Customize the VLAN ID to match the local environment
      InternalApiNetworkVlanID: 20


      # Customize the IP subnet to match the local environment
      TenantNetCidr: '172.16.0.0/24'
      # Customize the IP range to use for static IPs and VIPs
      TenantAllocationPools: [{'start': '172.16.0.4', 'end': '172.16.0.250'}]
      # Customize the VLAN ID to match the local environment
      TenantNetworkVlanID: 50
      # MTU of the underlying physical network. Neutron uses this value to
      # calculate MTU for all virtual network components. For flat and VLAN
      # networks, neutron uses this value without modification. For overlay
      # networks such as VXLAN, neutron automatically subtracts the overlay
      # protocol overhead from this value.
      TenantNetPhysnetMtu: 1500


      # Customize the IP subnet to match the local environment
      ExternalNetCidr: '10.0.0.0/24'
      # Customize the IP range to use for static IPs and VIPs
      # Leave room if the external network is also used for floating IPs
      ExternalAllocationPools: [{'start': '10.0.0.4', 'end': '10.0.0.250'}]
      # Gateway router for routable networks
      ExternalInterfaceDefaultRoute: '10.0.0.1'
      # Customize the VLAN ID to match the local environment
      ExternalNetworkVlanID: 10


      # Customize the IP subnet to match the local environment
      ManagementNetCidr: '10.0.1.0/24'
      # Customize the IP range to use for static IPs and VIPs
      ManagementAllocationPools: [{'start': '10.0.1.4', 'end': '10.0.1.250'}]
      # Gateway router for routable networks
      ManagementInterfaceDefaultRoute: '10.0.1.1'
      # Customize the VLAN ID to match the local environment
      ManagementNetworkVlanID: 60


      # Define the DNS servers (maximum 2) for the overcloud nodes
      # When the list is not set or empty, the nameservers on the ctlplane subnets will be used.
      # (ctlplane subnets nameservers are controlled by the ``undercloud_nameservers`` option in ``undercloud.conf``)
      DnsServers: ['135.1.1.111']
      BondInterfaceOvsOptions: "mode=active-backup"


neutron-nuage-config.yaml
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    parameter_defaults:
      NeutronNuageNetPartitionName: 'Nuage_Partition_16'
      NeutronNuageVSDIp: '192.168.24.118:8443'
      NeutronNuageVSDUsername: 'csproot'
      NeutronNuageVSDPassword: 'csproot'
      NeutronNuageVSDOrganization: 'csp'
      NeutronNuageBaseURIVersion: 'v6'
      NeutronNuageCMSId: 'a91a28b8-28de-436b-a665-6d08a9346464'
      UseForwardedFor: true
      NeutronPluginMl2PuppetTags: 'neutron_plugin_ml2,neutron_plugin_nuage'
      NeutronServicePlugins: 'NuagePortAttributes,NuageAPI,NuageL3'
      NeutronDBSyncExtraParams: '--config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --config-file /etc/neutron/plugins/nuage/plugin.ini'
      NeutronTypeDrivers: 'vxlan'
      NeutronNetworkType: 'vxlan'
      NeutronMechanismDrivers: 'nuage'
      NeutronPluginExtensions: 'nuage_network,nuage_subnet,nuage_port,port_security'
      NeutronFlatNetworks: '*'
      NeutronTunnelIdRanges: ''
      NeutronNetworkVLANRanges: ''
      NeutronVniRanges: '1001:2000'
      NovaOVSBridge: 'alubr0'
      NeutronMetadataProxySharedSecret: 'NuageNetworksSharedSecret'
      HeatEnginePluginDirs: ['/usr/lib/python2.7/site-packages/nuage-heat/']
      HorizonCustomizationModule: 'nuage_horizon.customization'
      HorizonVhostExtraParams:
        add_listen: true
        priority: 10
        access_log_format: '%a %l %u %t \"%r\" %>s %b \"%%{}{Referer}i\" \"%%{}{User-Agent}i\"'
        aliases: [{'alias': '%{root_url}/static/nuage', 'path': '/usr/lib/python3.6/site-packages/nuage_horizon/static'}, {'alias': '%{root_url}/static', 'path': '/usr/share/openstack-dashboard/static'}]
        directories: [{'path': '/usr/lib/python2.7/site-packages/nuage_horizon', 'options': ['FollowSymLinks'], 'allow_override': ['None'], 'require': 'all granted'}]
      ControllerExtraConfig:
        neutron::config::server_config:
          DEFAULT/ipam_driver:
            value: nuage_internal
          DEFAULT/enable_snat_by_default:
            value: false
        neutron::config::plugin_nuage_config:
          RESTPROXY/nuage_pat:
            value: legacy_disabled


neutron-sriov.yaml
~~~~~~~~~~~~~~~~~~~

Include this file in the ``openstack overcloud deploy`` command when you deploy the Overcloud:

::

    resource_registry:
      OS::TripleO::Services::NeutronSriovAgent: /usr/share/openstack-tripleo-heat-templates/deployment/neutron/neutron-sriov-agent-container-puppet.yaml
      OS::TripleO::Services::NeutronSriovHostConfig: /usr/share/openstack-tripleo-heat-templates/deployment/deprecated/neutron/neutron-sriov-host-config.yaml

    parameter_defaults:
      # Add PciPassthroughFilter to the scheduler default filters
      NovaSchedulerDefaultFilters: ['RetryFilter','AvailabilityZoneFilter','ComputeFilter','ComputeCapabilitiesFilter','ImagePropertiesFilter','ServerGroupAntiAffinityFilter','ServerGroupAffinityFilter','PciPassthroughFilter']
      NovaSchedulerAvailableFilters: ["nova.scheduler.filters.all_filters","nova.scheduler.filters.pci_passthrough_filter.PciPassthroughFilter"]
      NeutronPhysicalDevMappings: "physnet1:ens15f0,physnet2:ens15f1"

      # Number of VFs that needs to be configured for a physical interface
      NeutronSriovNumVFs: "ens15f0:7,ens15f1:7"
      ComputeSriovParameters:
        KernelArgs: "intel_iommu=on iommu=pt pci=realloc"
        TunedProfileName: ""
        NovaPCIPassthrough:
          - devname: "ens15f0"
            physical_network: "physnet1"
          - devname: "ens15f1"
            physical_network: "physnet2"


nova-nuage-config.yaml For a Virtual Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    parameter_defaults:
      NuageActiveController: '192.168.24.119'
      NuageStandbyController: '0.0.0.0'
      NovaPCIPassthrough: ""
      NovaOVSBridge: 'alubr0'
      NovaComputeLibvirtType: 'qemu'
      NovaIPv6: True
      NuageMetadataProxySharedSecret: 'NuageNetworksSharedSecret'
      NuageNovaApiEndpoint: 'internalURL'
      NovaComputeLibvirtVifDriver: 'nova.virt.libvirt.vif.LibvirtGenericVIFDriver'
      # VrsExtraConfigs can be used to configure extra parameters in /etc/default/openvswitch
      # For example to set "NETWORK_UPLINK_INTF" see below sample:
      # VrsExtraConfigs: {"NETWORK_UPLINK_INTF": "eno1"}
      VrsExtraConfigs: {}


nova-nuage-config.yaml For a KVM Setup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    parameter_defaults:
      NuageActiveController: '192.168.24.119'
      NuageStandbyController: '0.0.0.0'
      NovaPCIPassthrough: ""
      NovaOVSBridge: 'alubr0'
      NovaComputeLibvirtType: 'kvm'
      NovaIPv6: True
      NuageMetadataProxySharedSecret: 'NuageNetworksSharedSecret'
      NuageNovaApiEndpoint: 'internalURL'
      NovaComputeLibvirtVifDriver: 'nova.virt.libvirt.vif.LibvirtGenericVIFDriver'
      # VrsExtraConfigs can be used to configure extra parameters in /etc/default/openvswitch
      # For example to set "NETWORK_UPLINK_INTF" see below sample:
      # VrsExtraConfigs: {"NETWORK_UPLINK_INTF": "eno1"}
      VrsExtraConfigs: {}


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

For the scripts to patch the Overcloud qcow image, go to `stopgap-script <../../image-patching/stopgap-script>`_

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


Known Limitations
~~~~~~~~~~~~~~~~~

1. Using VrsExtraConfigs, you can configure extra parameters in /etc/default/openvswitch with these limitations:

   * Using the current approach, parameters that are not present in /etc/default/openvswitch by default may be configured.

   * VrsExtraConfigs can configure ACTIVE_CONTROLLER, STANDBY_CONTROLLER and BRIDGE_MTU by overwriting the values already assigned to them.

Links to Nuage and OpenStack Resources
---------------------------------------

* For the Heat templates used by OpenStack Platform Director, go to http://git.openstack.org/cgit/openstack/tripleo-heat-templates
* For the Puppet manifests, go to http://git.openstack.org/cgit/openstack/tripleo-heat-templates/tree/puppet
* For the nuage-puppet-modules RPM (nuage-puppet-modules-6.2.0), go to `nuage-puppet-modules <../../nuage-puppet-modules>`_
* For the scripts to patch the Overcloud qcow image, go to `nuage_image_patching_scripts <../../image-patching/nuage_image_patching_scripts>`_
* For the files and script to generate the CMS ID, go to `Generate CMS ID <../../nuage-tripleo-heat-templates/scripts/generate-cms-id>`_
