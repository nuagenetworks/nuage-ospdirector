FROM <undercloud-doamin-name>:8787/rhosp-rhel8/openstack-neutron-openvswitch-agent:<tag>

USER root

COPY RPM-GPG-KEY-Nuage /tmp/RPM-GPG-KEY-Nuage
COPY nuage.repo /etc/yum.repos.d/nuage.repo
RUN yum install --disablerepo "*" --enablerepo Nuage fp-vdev-remote networking-6wind -y && yum clean all

USER neutron
