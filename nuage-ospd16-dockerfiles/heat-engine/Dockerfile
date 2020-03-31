FROM <undercloud-doamin-name>:8787/rhosp-rhel8/openstack-heat-engine:<tag>

USER root

COPY RPM-GPG-KEY-Nuage /tmp/RPM-GPG-KEY-Nuage
COPY nuage.repo /etc/yum.repos.d/nuage.repo

RUN yum -y install --disablerepo "*" --enablerepo Nuage nuage-openstack-heat nuage-openstack-neutronclient && yum clean all



USER heat
