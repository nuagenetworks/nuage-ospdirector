.. _README:

.. include:: ../lib/doc-includes/pike-icons.inc

.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

.. highlight:: none


===================================
Minor Upgrade to Release 5.4.1 U8
===================================

.. contents::
   :local:
   :depth: 3


Use this documentation when upgrading between minor releases. The process applies to upgrades from Release 5.4.1 U5 to Release 5.4.1 U8+. During this process, the Nuage components can be updated at the same time.

It is assumed the operator is familiar with Red Hat OpenStack Platform Director upgrades, VSP installation, the distribution-specific installation and upgrade practices, and the specific requirements for operations in a production environment.


Upgrade Paths
-------------

In this release, you can upgrade only from Queens 5.4.1 U5 or later to Queens 5.4.1 U8.
    

These upgrade paths are not described in this document:
    
    * Upgrade from OpenStack releases before Queens 5.4.1 U5
    * Upgrade from VSP releases before Release 5.4.1 U5
    

If you are upgrading from a release earlier than Queens 5.4.1 U5, refer to the Nuage Queens upgrade documentation.


Basic Configuration
---------------------

The basic configuration includes:
   
   * An existing installed VSD and VSC upgraded to latest VSP release
   * A single OpenStack Controller node
   * One or more Compute nodes (hypervisors) running the VRS, SR-IOV, or AVRS nodes running Release 5.4.1 U5 or later
   


Before the Upgrade
--------------------

1. If you are upgrading an AVRS node, migrate all your VMs on the node to an AVRS Compute node that is not being upgraded. Perform the steps in the "Live Migrate a Virtual Machine" section in https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/migrating-virtual-machines-between-compute-nodes-osp#live-migrate-a-vm-osp

2. Create the following repositories:
    
    * Nuage_base_repo:
        
        - It contains Selinux-policy-nuage, nuage-bgp, Python-openvswitch-nuage, nuage-openstack-neutronclient, and nuage-puppet-modules.
        - Enable this repository on the OpenStack Controller nodes, the Compute VRS nodes, and the Nova Compute AVRS nodes.
    
    * Nuage_vrs_repo:
        
        - It contains nuage-metadata-agent and nuage-openvswitch.
        - Enable this repository on the OpenStack Controller node and the Nova Compute VRS nodes.
        
    
    * Nuage_avrs_repo:
        
        - It contains nuage-metadata-agent, nuage-openvswitch (avrs), nuage-selinux-avrs, and 6WIND packages.
        - Enable this repository on the Nova Compute AVRS nodes.
        
    


3. Get the latest Nuage docker images from the Red Hat Partner Registry by following these instructions: https://github.com/nuagenetworks/nuage-ospdirector/blob/OSPD13/Documentation/5.4.1/README.rst#phase-8-nuage-docker-containers

Upgrade Workflow
------------------

1. Back up the configuration files for your deployment.
    
     In the following example, all the templates and environment files for your deployment are in the /home/stack/nuage-ospdirector directory. To get new the Nuage 5.4.1 U8 nuage-ospdirector/nuage-tripleoheat-templates, back up the files before replacing the existing ones with new 5.4.1 U8 codebase.
    
    a. Back up the templates and environment files from /home/stack/nuage-ospdirector to /home/stack/nuage-ospdirector-bk.
       
       ::
       
           $ mv /home/stack/nuage-ospdirector /home/stack/nuage-ospdirector-bk
       
    
    
    b. Get the tar files for the upgrade one of these ways:
    
       * Download them from https://github.com/nuagenetworks/nuage-ospdirector/releases
       * Use ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b <release>``. For example, enter ``git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b osp-13.541U8.1``.
    

2. Make sure your all of the templates and environment files are updated with the environment values for your deployment.

    a. Get the environment values from the /home/stack/nuage-ospdirector-bk directory and update all the templates and environment files for the deployment, such as neutron-nuage/nova-nuage/compute-avrs and templates/compute-avrs-role.yaml.
    
    b. Make sure the resource_registry section of neutron-nuage-config.yaml contains the following line, which was added in Release 5.4.1 U8:
    
    ::
    
        OS::TripleO::Services::NeutronCorePlugin: ../docker/services/neutron-plugin-ml2-nuage.yaml
    
    

3. To update the Overcloud deployment, follow these instructions: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/keeping_red_hat_openstack_platform_updated/assembly-updating_the_overcloud


4. Run the image patching using the latest Nuage packages to update the Overcloud image. Follow these instructions: `README.md <../../image-patching/README.md>`_

