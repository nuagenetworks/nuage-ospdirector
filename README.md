# OSP Director Integration with Nuage

This repository provides information, architecture and deployment steps for integrating Red Hat OSP Director with Nuage VSP.

The repository includes:

1. **image-patching**: overcloud-full.qcow2 image patching resources.
2. **nuage-tripleo-heat-templates**: Heat template required for OSP Director and Nuage Integration.
3. **generate-cms-id**: CMS ID generation resources
4. **nuage-ospd13-dockerfiles**: (Deprecated : This is only required for 5.4.1u1 to 5.4.1u3). Starting from 5.4.1.U4, please refer to Red Hat Build Services for acquiring Nuage containers.
5. **Documentation**: The details of integration, architecture and deployment steps can be found under Documentation folders, as following.

    * For OSP Director 13 with + Nuage release 6.0.1: [README.rst](Documentation/6.0.1/README.rst)

    * For OSP Director 13 with + Nuage release 5.4.1.U4 and later: [README.rst](Documentation/5.4.1/README.rst)
        
    * For OSP Director 13 with + Nuage release 5.4.1.U1 to 5.4.1.U3: [README.rst](Documentation/5.4.1/README_U1_to_U3.rst)
    
    * For OSP Director 13 with + Nuage release before 5.4.1: [README.rst](Documentation/BEFORE_5.4.1/README.rst)
    
