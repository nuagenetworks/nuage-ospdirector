# Requirements:

Required packages are `libguestfs-tools` and `python-yaml`

```
yum install libguestfs-tools python-yaml -y
```


# Steps:

Copy the  folder image-patching from /home/stack/nuage-ospdirector/image-patching/ onto the hypervisor machine that is accessible to the nuage-rpms repo.

```
cd nuage_image_patching_scripts
```

Copy the `overcloud-full.qcow2` from undercloud-director /home/stack/images/ to this location and make a backup of overcloud-full.qcow2

    cp overcloud-full.qcow2 overcloud-full-bk.qcow2


This script takes in `nuage_patching_config.yaml` as input parameters:  Please configure the following parameters.

  * ImageName(required) is the name of the qcow2 image (for example, overcloud-full.qcow2)
  * NuageMajorVersion(required) is the Nuage Major Version and valid options are either '5.0' or '6.0'. Please enter '6.0'
  * DeploymentType(required) is for user to specify which deployment is it. Please choose from "vrs" or "ovrs" or "avrs"   
    a. For any combination of VRS and SRIOV deployments, please use deployment type as "vrs"   
    b. For any combination of AVRS, VRS and SRIOV deployments, please use deployment type as "avrs"   
    c. For OVRS deployments, please use deployment type as "ovrs"   
    d. For any combination of AVRS, OVRS, VRS and SRIOV, please use deployment type as ["avrs", "ovrs"]
  * RhelUserName(optional) is the user name for the RedHat Enterprise Linux subscription.
  * RhelPassword(optional) is the password for the RedHat Enterprise Linux subscription
  * RhelPool(optional) is the RedHat Enterprise Linux pool to which the base packages are subscribed. instructions to get this can be found [here](https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/installing-the-undercloud#registering-and-updating-your-undercloud) in the 2nd point.
  * RhelSatUrl(optional) is the url for the RedHat Satellite server.
  * RhelSatOrg(optional) is the organisation for the RedHat Satellite server.
  * RhelSatActKey(optional) is the activation key for the RedHat Satellite server. 
  
        Note: 
            If nuage packages are available using the activation key parameter RepoFile becomes optional.

  * RpmPublicKey(optional) is where you pass all the file path of the GPG key that you wish to add to your overcloud images before deploying the following packages.

        Note:
            Any Nuage package signing keys are delivered with other Nuage artifacts.  See "nuage-package-signing-keys-*.tar.gz".
            Make sure to copy GPG-Key file(s) to the same folder as "nuage_overcloud_full_patch.py" patching script directory.
  * RepoFile(required,optional for RedHat Satellite) is the name of the repository hosting the RPMs required for patching.
   
        Note (1): 
           Make sure to place repo file in the same folder as "nuage_overcloud_full_patch.py" patching script directory.
        Note (2):  
            If nuage packages are available using the activation key of a RedHat Satellite server, "RepoFile" becomes optional.

    **we are providing RepoFile exmaple `nuage_6.0_ospd13.repo.sample`**

    **RepoFile can contain only single Nuage repo with required Nuage packages and can also have extra repos with non Nuage packages:**
    Note: Currently, supported deployments are "vrs + avrs" or "ovrs". It is not necessary to have "ovrs" related packages for "avrs" deployments and vice versa.

        [nuage] repo should have following Nuage packages
            nuage-puppet-modules
            python-openvswitch-nuage
            selinux-policy-nuage
            selinux-policy-nuage-avrs (avrs)
            nuage-bgp
            nuage-openstack-neutronclient
            nuage-openvswitch (vrs)
            nuage-openvswitch-6wind (avrs)
            nuage-metadata-agent
            6wind packages (avrs)
            mstflint (ovrs)

        [extra] repo should have all the packages that we install as part of dependency packages:
           libvirt
           perl-JSON
           lldpad

  * logFileName is to pass log file name


 Now run the below command by providing required values:

    python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml


 ### Some examples:

###### 1. A/VRS deployment

1.1 Using same repos for nuage & 6wind package and No Redhat Subscription for dependent packages:

    a. I have configured different repos like following in my nuage_6.0_ospd13.repo :

        [nuage]
        name=nuage_osp13_6.0_nuage
        baseurl=http://1.2.3.4/nuage_osp13_6.0.3/nuage_repo
        enabled=1
        gpgcheck=1

        [extra]
        name=satellite
        baseurl=http://1.2.3.4/extra_repo
        enabled=1
        gpgcheck=1

    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        NuageMajorVersion: "6.0"
        DeploymentType: ["avrs"]
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_6.0_ospd13.repo'
        logFileName: "nuage_image_patching.log"

    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml

1.2 Using same repos for nuage & 6wind package and with Redhat Subscription for dependent packages:

    a. I have configured single repo like following in my nuage_6.0_ospd13.repo:

        [nuage]
        name=nuage_osp13_6.0_nuage
        baseurl=http://1.2.3.4/nuage_osp13_6.0.3/nuage_repo
        enabled=1
        gpgcheck=1

    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        NuageMajorVersion: "6.0"
        DeploymentType: ["avrs"]
        RhelUserName: 'abc'
        RhelPassword: '***'
        RhelPool: '1234567890123445'
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        logFileName: "nuage_image_patching.log"

    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml


###### 2. VRS Deployment

2.1 Using nuage repo for nuage packages and No Redhat Subscription for dependent packages:

    a. I have configured different repos like following in my nuage_6.0_ospd13.repo:

        [nuage]
        name=nuage_osp13_6.0_nuage
        baseurl=http://1.2.3.4/nuage_osp13_6.0.3/nuage_repo
        enabled=1
        gpgcheck=1

        [extra]
        name=satellite
        baseurl=http://1.2.3.4/extra_repo
        enabled=1
        gpgcheck=1

    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        NuageMajorVersion: "6.0"
        DeploymentType: ["vrs"]
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        logFileName: "nuage_image_patching.log"

    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml

2.2 Using nuage packages and with Redhat Subscription for dependent packages:

    a. I have configured single repo like following in my nuage_ospd13.repo:

        [nuage]
        name=nuage_osp13_6.0_nuage
        baseurl=http://1.2.3.4/nuage_osp13_6.0.3/nuage_repo
        enabled=1
        gpgcheck=1

    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        NuageMajorVersion: "6.0"
        DeploymentType: ["vrs"]
        RhelUserName: 'abc'
        RhelPassword: '***'
        RhelPool: '1234567890123445'
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        logFileName: "nuage_image_patching.log"

    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml


###### 3.OVRS Deployment

3.1 Using nuage repo for nuage packages and No Redhat Subscription for dependent packages:

    a. I have configured different repos like following in my nuage_6.0_ospd13.repo:

        [nuage]
        name=nuage_osp13_6.0_nuage
        baseurl=http://1.2.3.4/nuage_osp13_6.0.3/nuage_repo
        enabled=1
        gpgcheck=1

        [extra]
        name=satellite
        baseurl=http://1.2.3.4/extra_repo
        enabled=1
        gpgcheck=1

    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        NuageMajorVersion: "6.0"
        DeploymentType: ["ovrs"]
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        logFileName: "nuage_image_patching.log"

    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml

3.2 Using nuage packages and with Redhat Subscription for dependent packages:

    a. I have configured single repo like following in my nuage_ospd13.repo:

        [nuage]
        name=nuage_osp13_6.0_nuage
        baseurl=http://1.2.3.4/nuage_osp13_6.0.3/nuage_repo
        enabled=1
        gpgcheck=1

    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        NuageMajorVersion: "6.0"
        DeploymentType: ["ovrs"]
        RhelUserName: 'abc'
        RhelPassword: '***'
        RhelPool: '1234567890123445'
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        logFileName: "nuage_image_patching.log"

    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml

###### 3. Red Hat Satellite Deployment

3.1 Using local repos for nuage packages and Red Hat Satellite for dependent packages:

    a. The Red Hat Satellite activation key is configured 
        with Red Hat OpenStack Platform subscription enabled

    b. I have configured four different repos like following in my nuage_ospd13.repo:
        
        [nuage]
        name=nuage_osp13_6.0_nuage
        baseurl=http://1.2.3.4/nuage_osp13_6.0.3/nuage_repo
        enabled=1
        gpgcheck=1

        [extra]
        name=satellite
        baseurl=http://1.2.3.4/extra_repo
        enabled=1
        gpgcheck=1
    
    c. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        NuageMajorVersion: "6.0"
        DeploymentType: ["ovrs"]
        RhelSatUrl: 'https://satellite.example.com'
        RhelSatOrg: 'example_organization'
        RhelSatActKey: 'example_key'
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        VRSRepoNames: ['nuage_vrs']
        logFileName: "nuage_image_patching.log"
    
    d. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml

3.2 Using Red Hat Satellite for nuage packages and dependent packages:

    a. The Red Hat Satellite activation key is configured 
        - with Red Hat OpenStack Platform subscription enabled
        - with a Nuage product containing the nuage packages
          and the Nuage product subscription enabled

    c. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        NuageMajorVersion: "6.0"
        DeploymentType: ["ovrs"]
        RhelSatUrl: 'https://satellite.example.com'
        RhelSatOrg: 'example_organization'
        RhelSatActKey: 'example_key'
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        logFileName: "nuage_image_patching.log"
    
    d. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml




If image patching fails for some reason then remove the partially patched overcloud-full.qcow2 and create a copy of it from backup image before retrying image patching again.

    rm overcloud-full.qcow2
    cp overcloud-full-bk.qcow2 overcloud-full.qcow2


In order to verify that  machine-id is clear in the overcloud image, run the following command and you should see empty output:

        guestfish -a overcloud-full.qcow2 run : mount /dev/sda / : cat /etc/machine-id

Now you can copy back the patched image to /home/stack/images/ on undercloud-director


Run the below commands:

```
[stack@director ~]$ source ~/stackrc
(undercloud) [stack@director ~]$ openstack image list
```

1. If above command returns null, run the below command
` (undercloud) [stack@director images]$ openstack overcloud image upload --image-path /home/stack/images/`

2. If it returns something like below
```
+--------------------------------------+------------------------+
| ID                                   | Name                   |
+--------------------------------------+------------------------+
| 765a46af-4417-4592-91e5-a300ead3faf6 | bm-deploy-ramdisk      |
| 09b40e3d-0382-4925-a356-3a4b4f36b514 | bm-deploy-kernel       |
| ef793cd0-e65c-456a-a675-63cd57610bd5 | overcloud-full         |
| 9a51a6cb-4670-40de-b64b-b70f4dd44152 | overcloud-full-initrd  |
| 4f7e33f4-d617-47c1-b36f-cbe90f132e5d | overcloud-full-vmlinuz |
+--------------------------------------+------------------------+
```

then run the below command

```
(undercloud) [stack@director images]$ openstack overcloud image upload --update-existing --image-path /home/stack/images/
(undercloud) [stack@director images]$ openstack overcloud node configure $(openstack baremetal node list -c UUID -f value)
```
