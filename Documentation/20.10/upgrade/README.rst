.. Don't use default python highlighting for code blocks http://www.sphinx-doc.org/en/stable/markup/code.html

===================================
Minor Update to Release 20.10.8
===================================

.. contents::
   :local:
   :depth: 3


Use this documentation when updating between nuage minor releases. The process applies to updates from Release 20.10.5 to Release 20.10.8. During this process, the Nuage components are updated to 20.10.8.

It is assumed the operator is familiar with Red Hat OpenStack Platform Director updates, VSP installation, the distribution-specific installation and update practices, and the specific requirements for operations in a production environment.


Update Paths
-------------

In this release, you can update only from OSP Director 16.1.6 + 20.10.5 to OSP Director 16.1.7 + 20.10.8.


These update paths are not described in this document:

    * Update from OpenStack releases before Train 20.10.5
    * Update from VSP releases before Release 20.10.5


Basic Configuration
---------------------

The basic configuration includes:

   * One or more Controller node(s)
   * One or more Compute nodes (hypervisors) running the VRS, SR-IOV, AVRS nodes running Release 20.10.8



Before the Update
--------------------


1. Get the new Nuage VSP RPMs

The list of RPMs needed can be found in `Phase 2.1: Download the Nuage VSP RPMs` of the Fresh install guide for 20.10.8.
Put these PRMs in a repository and synchronize it with, or directly upload these packages to Red Hat Satellite.

Follow the Fresh install guide for 20.10.8 step `Phase 2.1: Download the Nuage VSP RPMs`.



2. Ensure both undercloud and overcloud have the new repositories enabled and old Nuage repositories disabled

This steps depends a bit on how Red Hat Satellite is used.
There are two options here, either by updating the current activation key with the new RPMs (scenario A), or multiple
activation keys are used to separate the Nuage versions (scenario B).

An tested example of how Scenario B can be solved will be explained here:

The reason these steps are needed is that using the `rhsm_force_register` setting is only applied at the end of the
update. While to update the Nuage RPMs we need this to be done before or during.

Using the below guide, we can create an inventory file of the setup overcloud.
https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.1/html/keeping_red_hat_openstack_platform_updated/preparing-for-a-minor-update_keeping-updated#locking-the-environment-to-a-red-hat-enterprise-linux-release_keeping-updated

::

    tripleo-ansible-inventory --ansible_ssh_user heat-admin --static-yaml-inventory ~/inventory.yaml

This inventory file we can now use in some automation scripts. Here is an example of how one can force a new
activation key onto the deployment.


::

    <set-rh-key.yaml>
    - hosts: all
      gather_facts: false
      tasks:
        - name: update satellite activation key
          command: subscription-manager register --force --activationkey=nuage-20.10.8-16.1 --org=<>
          become: true

This file can then be run using:

::

    ansible-playbook -i inventory.yaml -f 25 set-rh-key.yaml --limit overcloud

The example limits the playbook to only the overcloud, but one should also make sure some of the 20.10.8
Nuage RPMs are available on the undercloud. This action depends a lot on how your setup is done

For the undercloud this can be simply done manually.

Afterwards a spot check should be done on the overcloud and or undercloud to see if the new 20.10.8 RPMs are available.


Update Workflow
------------------

1. Back up the configuration files for your deployment.

     In the following example, all the templates and environment files for your deployment are in the /home/stack/nuage-ospdirector directory. To get new the Nuage 20.10.8 nuage-ospdirector/nuage-tripleoheat-templates, back up the files before replacing the existing ones with new 20.10.8 codebase.

    a. Back up the templates and environment files from /home/stack/nuage-ospdirector to /home/stack/nuage-ospdirector-bk.

       ::

           $ mv /home/stack/nuage-ospdirector /home/stack/nuage-ospdirector-bk


2. Update nuage-tripleo-heat-templates package by using

::

    $ sudo yum update nuage-tripleo-heat-templates

3. Copy nuage-tripleo-heat-templates to /home/stack before customizing environment files

::

    $ cp -r /usr/share/nuage-tripleo-heat-templates /home/stack/



4. Regenerate roles data file by following below instructions

Follow the instructions `Phase 3.4: Create the Dataplane Roles and Update the Node Profiles` of fresh install


5. Make sure your all of the templates and environment files are updated with the environment values for your deployment.

Get the environment values from the /home/stack/nuage-ospdirector-bk directory and update all the templates and environment files for the deployment, such as neutron-nuage/nova-nuage/compute-avrs/ovs-hw-offload/mellanox-environment.


6. Get the latest Nuage docker images from the Red Hat Partner Registry

These can be obtained by following these instructions in `Phase 2.3: Prepare Nuage Containers` from `20.10/README.rst <../../README.rst>`_
If AVRS is deployed, follow `Phase 2.4: Pull AVRS Containers` from the Red Hat Catalog as well.


7. To update the Overcloud deployment, follow these instructions: https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/16.1/html/keeping_red_hat_openstack_platform_updated/assembly-updating_the_overcloud

Here it is important to use the container-image-prepare file containing the references to Nuage containers resulted by `Step 6`

8. Reboot overcloud as described in the Red Hat Instructions

9. Once the overcloud update is complete, update nuage-topology-collector using:

    ::

        $ sudo yum update nuage-topology-collector -y

