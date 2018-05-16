Steps:

1. Download all files and folders from [here](https://github.mv.usa.alcatel.com/Integration/Nuage-OSPD-Dockerfiles/tree/master/nuage-ospd13-dockerfiles) to undercloud machine
2. Open nuage_docker_config.yaml and pass values to each keys. An example of this file is shown below

Registry: 10.31.137.88:4000/registry.distributed-ci.io   
OSPD_Version: 13   
Tag: 2018-04-10.2   
EnableProxy: false   
RepoBaseUrl: http://135.227.146.166/5.2R2U1/queens   
DockerImages: 'nuage-heat-api-cfn nuage-heat-api nuage-heat-engine nuage-horizon nuage-neutron-api'    

3. Run the following comand to generate the Nuage Dockerfiles
"python generate_nuage_dockerfiles.py nuage_docker_config.yaml"

4. Verfiy that all Nuage Dockerfiles are generated and present in nuage-dockerfiles folder.
