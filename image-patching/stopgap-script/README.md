#Steps:

Clone this repo onto the machine that is accessible to the nuage-rpms repo and make sure the machine also has `libguestfs-tools` installed.

```
yum install libguestfs-tools -y
git clone https://github.com/nuagenetworks/nuage-ospdirector.git
cd nuage-ospdirector
git checkout OSPD13
cd image-patching/stopgap-script/
```

Copy the `overcloud-full.qcow2` from undercloud-director /home/stack/images/ to this location and make a backup of overcloud-full.qcow2    

    cp overcloud-full.qcow2 overcloud-full-bk.qcow2`


Now run the below command by providing required values   
    
### With GPG Key(s)  

Make sure to copy GPG-Key file(s) to the same folder as "nuage_overcloud_full_patch.py" patching script location.

**Note**: Any Nuage package signing keys are delivered with other Nuage artifacts.  See "nuage-package-signing-keys-*.tar.gz".

For single GPG-key run the below command
    
    python nuage_overcloud_full_patch.py --RhelUserName='<value>' --RhelPassword='<value>' --RhelPool=<pool-id> --ImageName='<value>' --RepoFile=<repo_file> --VRSRepoName=<vrs_repo_name1> --VRSRepoName=<vrs_repo_name2> --RpmPublicKey='GPG-Key'


For AVRS Integration with single GPG-key, please run below command

    python nuage_overcloud_full_patch.py --RhelUserName='<value>' --RhelPassword='<value>' --RhelPool=<pool-id> --ImageName='<value>' --RepoFile=<repo_file> --VRSRepoName=<vrs_repo_name1> --VRSRepoName=<vrs_repo_name2> --AVRSRepoName=<avrs_repo_name1> --AVRSRepoName=<avrs_repo_name2> --RpmPublicKey='GPG-Key'


For passing multiple GPG-keys, please repeat option "--RpmPublicKey" to set multiple GPG keys, for example

    python nuage_overcloud_full_patch.py --RhelUserName='<value>' --RhelPassword='<value>' --RhelPool=<pool-id> --ImageName='<value>' --RepoFile=<repo_file> --VRSRepoName=<vrs_repo_name1> --VRSRepoName=<vrs_repo_name2> --RpmPublicKey='GPG-Key1' --RpmPublicKey='GPG-Key2'


For AVRS Integration with multiple GPG-keys, please run below command

    python nuage_overcloud_full_patch.py --RhelUserName='<value>' --RhelPassword='<value>' --RhelPool=<pool-id> --RepoFile=<repo_file> --VRSRepoName=<vrs_repo_name1> --VRSRepoName=<vrs_repo_name2> --AVRSRepoName=<avrs_repo_name1> --AVRSRepoName=<avrs_repo_name2> --ImageName='<value>' --RpmPublicKey='GPG-Key1' --RpmPublicKey='GPG-Key2'


### Without GPG Key

    python nuage_overcloud_full_patch.py --RhelUserName='<value>' --RhelPassword='<value>' --RhelPool=<pool-id> --ImageName='<value>'  --RepoFile=<repo_file> --VRSRepoName=<vrs_repo_name1> --VRSRepoName=<vrs_repo_name2>  --no-signing-key

For AVRS Integration, Please run below command

    python nuage_overcloud_full_patch.py --RhelUserName='<value>' --RhelPassword='<value>' --RhelPool=<pool-id> --ImageName='<value>'  --RepoFile=<repo_file> --VRSRepoName=<vrs_repo_name1> --VRSRepoName=<vrs_repo_name2>  --AVRSRepoName=<avrs_repo_name1> --AVRSRepoName=<avrs_repo_name2>  --no-signing-key

This script takes in following input parameters:   
  * RhelUserName is the user name for the RedHat Enterprise Linux subscription.
  * RhelPassword is the password for the RedHat Enterprise Linux subscription
  * RepoFile is the name of the repository hosting the RPMs required for patching. 
        
  **We are providing RepoFile exmaple `nuage_ospd13.repo.sample`** 
  
  **Please make sure you enable `nuage` repo by default**. `nuage` repo contain following packages:
  
        nuage-puppet-modules
        selinux-policy-nuage 
        nuage-bgp 
        nuage-openstack-neutronclient
        libvirt
        perl-JSON
        lldpad

  * VRSRepoName will contain Repo Names containing following nuage packages:

        nuage-openvswitch 
        nuage-metadata-agent
  
  * AVRSRepoName will contain Repo Names containing following packages:

        nuage-openvswitch
        nuage-metadata-agent
        6wind packages
  
  **Note:** You can enable some other repos as well in the RepoFile that you wish to enable **(enabled=1)** it by default in addition to other packages. 
  
  * RhelPool is the RedHat Enterprise Linux pool to which the base packages are subscribed. instructions to get this can be found [here](https://access.redhat.com/documentation/en-us/red_hat_openstack_platform/13/html/director_installation_and_usage/installing-the-undercloud#registering-and-updating-your-undercloud) in the 2nd point.
  * ImageName is the name of the qcow2 image (for example, overcloud-full.qcow2)
  * Version is the OpenStack Platform director version (for Queens, the version is 13).
  * RpmPublicKey is the GPG-Key file name (repeat option to set multiple RPM GPG Keys).
  * no-signing-key is 'Image patching proceeds with package signature verification disabled'
  * logFile is to pass log file name

If image patching fails for some reason then remove the partially patched overcloud-full.qcow2 and create a copy of it from backup image before retrying image patching again.   

    rm overcloud-full.qcow2
    cp overcloud-full-bk.qcow2 overcloud-full.qcow2


Once the patching is done successfully copy back the patched image to /home/stack/images/ on undercloud-director   

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
