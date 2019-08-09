# Requirements:

Required packages are `libguestfs-tools` and `python-yaml`

```
yum install libguestfs-tools python-yaml -y
```


# Steps:

Clone this repo onto the hypervisor machine that is accessible to the nuage-rpms repo.

```
git clone https://github.com/nuagenetworks/nuage-ospdirector.git
cd nuage-ospdirector
git checkout OSPD13_VRS_offload
cd image-patching/stopgap-script/
```

Copy the `overcloud-full.qcow2` from undercloud-director /home/stack/images/ to this location and make a backup of overcloud-full.qcow2    

    cp overcloud-full.qcow2 overcloud-full-bk.qcow2


This script takes in `nuage_patching_config.yaml` as input parameters:  Please configure the following parameters. 
  
  * ImageName(required) is the name of the qcow2 image (for example, overcloud-full.qcow2)
  * DeploymentType(required) is for user to specify which deployment is it. Please choose from "vrs" or "ovrs" or "avrs"
        
        Note: Currently Nuage doesn't support both AVRS and OVRS deployment together
  * RhelUserName(optional) is the user name for the RedHat Enterprise Linux subscription.
  * RhelPassword(optional) is the password for the RedHat Enterprise Linux subscription
  * RhelPool(optional) is the RedHat Enterprise Linux pool to which the base packages are subscribed. instructions to get this can be found [here](https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/installing-the-undercloud#registering-and-updating-your-undercloud) in the 2nd point.
  * RpmPublicKey(optional) is where you pass all the file path of the GPG key that you wish to add to your overcloud images before deploying the following packages.
        
        Note: 
            Any Nuage package signing keys are delivered with other Nuage artifacts.  See "nuage-package-signing-keys-*.tar.gz". Mellanox signing keys can be found on their website.
            Make sure to copy GPG-Key file(s) to the same folder as "nuage_overcloud_full_patch.py" patching script directory. 
  * RepoFile(required) is the name of the repository hosting the RPMs required for patching.
   
        Note: 
           Make sure to place repo file in the same folder as "nuage_overcloud_full_patch.py" patching script directory.
                    
    **we are providing RepoFile exmaple `nuage_ospd13.repo.sample`** 
    
    **RepoFile can contain multiple repos. Please read following for more information about the repos in RepoFile:**
  
        [nuage] repo should have: (We recommend user to enable this repo "enabled=1" by default as below packages will be installed via this repo)
            nuage-puppet-modules
            selinux-policy-nuage 
            nuage-bgp 
            nuage-openstack-neutronclient
        
        [nuage_vrs] repo should have:       
            nuage-openvswitch 
            nuage-metadata-agent
        
        [kernel repo] should have all the packages that are provided by Redhat as Kernel Hotfix.
            kernel
            kernel-tools
            kernel-tools-libs
            python-perf 
        
        [mlnx repo] should have all the packages that are provided by Mellanox.
            kmod-mlnx-en
            mlnx-en-utils
            mstflint  
            os-net-config
        
        [nuage_avrs] should have all the packages provided by Nuage for openvswitch and 6wind rpms.
            nuage-openvswitch 
            nuage-metadata-agent
            6wind packages
        
        [extra] repo should have all the packages that we install as part of dependency packages:
           libvirt
           perl-JSON
           lldpad
  
  * VRSRepoNames will contain Repo Names containing following Nuage O/VRS packages:

        nuage-openvswitch 
        nuage-metadata-agent
        
  * AVRSRepoNames will contain Repo Names containing following Nuage A/VRS and 6wind packages:

        nuage-openvswitch 
        nuage-metadata-agent
        6wind packages  
        
  * KernelRepoNames will contain Repo Names containing following packages:

        kernel
        kernel-tools
        kernel-tools-libs
        python-perf

  * MellanoxRepoNames will contain Repo Names containing following packages:

        kmod-mlnx-en
        mlnx-en-utils
        mstflint
        os-net-config
         
  **Note:** 
  
    RepoFile can also have additional repos enabled that user wish to enable while patching. 
    It is highly recommended to disable AVRS and VRS by default (enabled =0) in the repo file and provide the AVRSRepoName & VRSRepoName in config file.  
 
  * KernelHF, if set to True, kernel on the overcloud image will be updated to latest version present in KernelRepoNames. 
  
  * logFileName is to pass log file name


Now run the below command by providing required values:

    python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml


### Some examples:

###### 1. A/VRS deployment 

1.1 Using different repos for nuage & 6wind package and No Redhat Subscription for dependent packages:

    a. I have configured four different repos like following in my nuage_ospd13.repo:
        
        [nuage]
        name=nuage_osp13_5.4.1.u4_nuage
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_extra
        enabled=1
        gpgcheck=1 
               
        [nuage_vrs]
        name=nuage_osp13_5.4.1.u4_nuage_vrs
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_vrs
        enabled=0
        gpgcheck=1
                
        [nuage_avrs]
        name=nuage_osp13_5.4.1.u4_nuage_avrs
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/avrs
        enabled=0
        gpgcheck=1
        
        [extra]
        name=satellite
        baseurl=http://1.2.3.4/extra_repo
        enabled=1
        gpgcheck=1
    
    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        DeploymentType: ["avrs"]
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        VRSRepoNames: ['nuage_vrs']
        AVRSRepoNames: ['nuage_avrs']
        logFileName: "nuage_image_patching.log"
        
    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml

1.2 Using different repos for nuage & 6wind package and with Redhat Subscription for dependent packages:

    a. I have configured four different repos like following in my nuage_ospd13.repo:
        
        [nuage]
        name=nuage_osp13_5.4.1.u4_nuage
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_extra
        enabled=1
        gpgcheck=1 
               
        [nuage_vrs]
        name=nuage_osp13_5.4.1.u4_nuage_vrs
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_vrs
        enabled=0
        gpgcheck=1
                
        [nuage_avrs]
        name=nuage_osp13_5.4.1.u4_nuage_avrs
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/avrs
        enabled=0
        gpgcheck=1
        
    
    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        DeploymentType: ["avrs"]
        RhelUserName: 'abc'
        RhelPassword: '***'
        RhelPool: '1234567890123445'
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        VRSRepoNames: ['nuage_vrs']
        AVRSRepoNames: ['nuage_avrs']
        logFileName: "nuage_image_patching.log"
    
    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml


###### 2. O/VRS Deployment

2.1 Using different repos for nuage & kernel & mellanox packages and No Redhat Subscription for dependent packages:

    a. I have configured four different repos like following in my nuage_ospd13.repo:
        
        [nuage]
        name=nuage_osp13_5.4.1.u4_nuage
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_extra
        enabled=1
        gpgcheck=1 
               
        [nuage_vrs]
        name=nuage_osp13_5.4.1.u4_nuage_ovrs
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_vrs
        enabled=0
        gpgcheck=1
                
        [mlnx]
        name=nuage_osp13_5.4.1.u4_mlnx
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/mlnx/
        enabled=0
        gpgcheck=1
        
        [kernel]
        name=nuage_osp13_5.4.1.u4_kernel
        baseurl=http://1.2.3.4/kernel/
        enabled=0
        gpgcheck=1
        
        [extra]
        name=satellite
        baseurl=http://1.2.3.4/extra_repo
        enabled=1
        gpgcheck=1
    
    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        DeploymentType: ["ovrs"]
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        VRSRepoNames: ['nuage_vrs']
        MellanoxRepoNames: ['mlnx']
        KernelRepoNames: ['kernel']
        KernelHF: True
        logFileName: "nuage_image_patching.log"
    
    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml
    
2.2 Using different repos for nuage & kernel & mellanox packages and with Redhat Subscription for dependent packages:

    a. I have configured four different repos like following in my nuage_ospd13.repo:
        
        [nuage]
        name=nuage_osp13_5.4.1.u4_nuage
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_extra
        enabled=1
        gpgcheck=1 
               
        [nuage_vrs]
        name=nuage_osp13_5.4.1.u4_nuage_ovrs
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_vrs
        enabled=0
        gpgcheck=1
                
        [mlnx]
        name=nuage_osp13_5.4.1.u4_mlnx
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/mlnx/
        enabled=0
        gpgcheck=1
        
        [kernel]
        name=nuage_osp13_5.4.1.u4_kernel
        baseurl=http://1.2.3.4/kernel/
        enabled=0
        gpgcheck=1
        
        [extra]
        name=satellite
        baseurl=http://1.2.3.4/extra_repo
        enabled=1
        gpgcheck=1
    
    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        DeploymentType: ["ovrs"]
        RhelUserName: 'abc'
        RhelPassword: '***'
        RhelPool: '1234567890123445'
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        VRSRepoNames: ['nuage_vrs']
        MellanoxRepoNames: ['mlnx']
        KernelRepoNames: ['kernel']
        KernelHF: True
        logFileName: "nuage_image_patching.log"
    
    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml

2.2 Using different repos for nuage and same repo for kernel mellanox packages and No Redhat Subscription for dependent packages:

    a. I have configured four different repos like following in my nuage_ospd13.repo:
        
        [nuage]
        name=nuage_osp13_5.4.1.u4_nuage
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_extra
        enabled=1
        gpgcheck=1 
               
        [nuage_vrs]
        name=nuage_osp13_5.4.1.u4_nuage_ovrs
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/nuage_vrs
        enabled=0
        gpgcheck=1
                
        [mlnx_kernel]
        name=nuage_osp13_5.4.1.u4_mlnx
        baseurl=http://1.2.3.4/nuage_osp13_5.4.1/mlnx_kernel/
        enabled=0
        gpgcheck=1
                
        [extra]
        name=satellite
        baseurl=http://1.2.3.4/extra_repo
        enabled=1
        gpgcheck=1
    
    b. Configure nuage_patching_config.yaml like:

        ImageName: "overcloud-full.qcow2"
        DeploymentType: ["ovrs"]
        RpmPublicKey: ['RPM-GPG-Nuage-key', 'RPM-GPG-SOMEOTHER-key']
        RepoFile: './nuage_ospd13.repo'
        VRSRepoNames: ['nuage_vrs']
        MellanoxRepoNames: ['mlnx_kernel']
        KernelRepoNames: ['mlnx_kernel']
        KernelHF: True
        logFileName: "nuage_image_patching.log"
    
    c. Run: python nuage_overcloud_full_patch.py --nuage-config nuage_patching_config.yaml

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
