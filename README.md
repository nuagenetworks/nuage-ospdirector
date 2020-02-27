# OSP Director Integration with Nuage

This repository provides information, architecture, and deployment steps for integrating Red Hat OpenStack Platform Director (OSPD) with Nuage VSP.

All the Nuage OSPD integration artifacts are released as github releases. You can download corresponding **tar.gz** files for specific nuage release at [Release](https://github.com/nuagenetworks/nuage-ospdirector/releases) 

Artifacts in the releases includes:

* **image-patching**: overcloud-full.qcow2 image patching resources
* **nuage-tripleo-heat-templates**: Heat template required for OSPD and Nuage integration
* **generate-cms-id**: CMS ID generation resources
* **Documentation**: The detailed integration, architecture, and deployment procedures are in the Documentation folders.

**IMPORTANT NOTE**:

If you are a git user please follow the following command to clone a specific nuage release instead of downloading **tar.gz**. For example:

Nuage release: 5.4.1U6

    git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b osp-13.541U6.1

Nuage release: 6.0.2

    git clone https://github.com/nuagenetworks/nuage-ospdirector.git -b osp-13.602.1