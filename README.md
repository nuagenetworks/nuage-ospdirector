# OSP Director Integration with Nuage

This repository provides information, architecture and deployment steps for integrating Red Hat OSP Director with Nuage VSP.

Starting from Nuage **5.4.1U6** and **6.0.2**, all the Nuage OSPD Integration artifacts are released as github releases. Please download corresponding **tar.gz** files for specific nuage release at [Release](https://github.com/nuagenetworks/nuage-ospdirector/releases) 

Artifacts in the releases includes:

1. **image-patching**: overcloud-full.qcow2 image patching resources.
2. **nuage-tripleo-heat-templates**: Heat template required for OSP Director and Nuage Integration.
3. **generate-cms-id**: CMS ID generation resources
4. **nuage-ospd13-dockerfiles**: (Deprecated : This is only required for 5.4.1u1 to 5.4.1u3). Starting from 5.4.1.U4, please refer to Red Hat Build Services for acquiring Nuage containers.
5. **Documentation**: The details of integration, architecture and deployment steps can be found under Documentation folders.

For deploying any 5.0 Nuage release until 5.4.1U6, please download tar.gz from this [release](https://github.com/nuagenetworks/nuage-ospdirector/releases/tag/osp-13.541U6.1) for above mentioned nuage artifacts and documentation. 

Below is the documentation directory structure to follow.
 
   * For OSP Director 13 with + Nuage release 5.4.1.U4 - U6 : Documentation/5.4.1/README.rst
        
   * For OSP Director 13 with + Nuage release 5.4.1.U1 to 5.4.1.U3: Documentation/5.4.1/README_U1_to_U3.rst
    
   * For OSP Director 13 with + Nuage release before 5.4.1: Documentation/BEFORE_5.4.1/README.rst  

For deploying any 6.0 Nuage release until 6.0.2,  please download tar.gz from this [release](https://github.com/nuagenetworks/nuage-ospdirector/releases/tag/osp-13.602.1) for above mentioned nuage artifacts and documentation.     

Below is the documentation directory structure to follow.


   * For OSP Director 13 with + Nuage release 6.0.1: Documentation/6.0.1/README.rst
    
   * For OSP Director 13 with + Nuage release 6.0.2: Documentation/6.0.2/README.rst

 
