<h3> The Patching already should take care of following: </h3>

<b> Note: Use the greatest diff version that is less than or equal to the current openstack-tripleo-heat-templates version. </b>


* Make sure [avrs-first-boot.yaml](https://github.com/nuagenetworks/nuage-ospdirector/blob/OSPD13/avrs/avrs-first-boot.yaml) is present under /usr/share/openstack-tripleo-heat-templates/firstboot/ .

* Make sure [avrs-post.yaml](https://github.com/nuagenetworks/nuage-ospdirector/blob/OSPD13/avrs/avrs-post.yaml) is present under /usr/share/openstack-tripleo-heat-templates/extraconfig/post_deploy/ .

* Based on the openstack-tripleo-heat-templates version, compare the appropriate `nova-compute-avrs-<openstack-tripleo-heat-templates version>.yaml` to /usr/share/openstack-tripleo-heat-templates/docker/services/ as nova-compute-avrs.yaml .
Note: For openstack-tripleo-heat-templates version `8.0.4-20`, `8.0.7-4` and `8.0.7-21` refer to nova-compute-avrs-8.0.4-20.yaml

* Create an environment file as [avrs-environment.yaml](https://github.com/nuagenetworks/nuage-ospdirector/blob/OSPD13/avrs/avrs-environment.yaml) under /usr/share/openstack-tripleo-heat-templates/environments/.

* Mapping of environment file parameters to the **fast-path.env** parameters:

<pre>
FastPathMask           =====>    FP_MASK
FastPathNics           =====>    FP_PORTS
CorePortMapping        =====>    CORE_PORT_MAPPING
FastPathMemory         =====>    FP_MEMORY
VmMemory               =====>    VM_MEMORY
NbMbuf                 =====>    NB_MBUF
FastPathOffload        =====>    FP_OFFLOAD
FastPathNicDescriptors =====>    FPNSDK_OPTIONS
FastPathDPVI           =====>    DPVI_MASK
FastPathOptions        =====>    FP_OPTIONS
</pre>

* Modify the code in /usr/share/openstack-tripleo-heat-templates/overcloud-resource-registry-puppet.j2.yaml to define Post deployment steps for the specific role.

<pre>

  OS::TripleO::Services::MongoDb: puppet/services/disabled/mongodb-disabled.yaml
  OS::TripleO::Services::NovaApi: docker/services/nova-api.yaml
  OS::TripleO::Services::NovaCompute: docker/services/nova-compute.yaml
  <b>OS::TripleO::Services::NovaComputeAvrs: docker/services/nova-compute-avrs.yaml</b>                   <====== ADD THIS LINE
  OS::TripleO::Services::NovaConductor: docker/services/nova-conductor.yaml
  OS::TripleO::Services::NovaConsoleauth: docker/services/nova-consoleauth.yaml

</pre>


<pre>
  # Hooks for operator extra config
  # NodeUserData == Cloud-init additional user-data, e.g cloud-config
  # role::NodeUserData == Role specific cloud-init additional user-data
  # ControllerExtraConfigPre == Controller configuration pre service deployment
  # NodeExtraConfig == All nodes configuration pre service deployment
  # NodeExtraConfigPost == All nodes configuration post service deployment
  OS::TripleO::NodeUserData: firstboot/userdata_default.yaml
{% for role in roles %}
  OS::TripleO::{{role.name}}::NodeUserData: firstboot/userdata_default.yaml
  <b>OS::TripleO::{{role.name}}ExtraConfigPost: extraconfig/post_deploy/default.yaml</b>                   <====== ADD THIS LINE
{% endfor %}
  OS::TripleO::NodeTLSCAData: OS::Heat::None
  OS::TripleO::NodeTLSData: OS::Heat::None
  OS::TripleO::NodeExtraConfig: puppet/extraconfig/pre_deploy/default.yaml
  OS::TripleO::NodeExtraConfigPost: extraconfig/post_deploy/default.yaml
</pre>

* Modify the code in /usr/share/openstack-tripleo-heat-templates/common/deploy-steps.j2 to include role specific ExtraConfigPost.

<pre>
  # Note, this should be the last step to execute configuration changes.
  # Ensure that all {{role.name}}ExtraConfigPost steps are executed
  # after all the previous deployment steps.
  {{role.name}}ExtraConfigPost:
    depends_on:
  {%- for dep in enabled_roles %}
      - {{dep.name}}Deployment_Step{{deploy_steps_max - 1}}
  {%- endfor %}
    <b>type: OS::TripleO::{{role.name}}ExtraConfigPost</b>                                                <======= MODIFY THIS LINE
    properties:
        servers: {get_param: [servers, {{role.name}}]}
</pre>
