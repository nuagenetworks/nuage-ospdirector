# OSP Director integration with Nuage

This repository provides information, architecture and deployment steps for integrating OSP Director with Nuage VSP.

The repository includes:

1. tripleo: Heat-template changes required for OSP Director and Nuage integration

2. puppet-neutron: Puppet-Neutron changes for Nuage integration

3. puppet-nova: Puppet-Nova changes for Nuage integration

4. image-patching: overcloud-full.qcow2 image patching resources

Please always deploy from a Release tag, e.g. osp-13.603.1 for OSPD13 with Nuage 6.0.3.

If, for engineering purposes, you are interested in the latest dev version of a given branch, select HEAD of branch, e.g. OSPD13.
