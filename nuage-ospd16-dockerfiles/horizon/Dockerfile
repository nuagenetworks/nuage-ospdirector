FROM <undercloud-doamin-name>:8787/rhosp-rhel8/openstack-horizon:<tag>

COPY RPM-GPG-KEY-Nuage /tmp/RPM-GPG-KEY-Nuage
COPY nuage.repo /etc/yum.repos.d/nuage.repo
RUN yum -y install --disablerepo "*" --enablerepo Nuage nuage-openstack-horizon nuage-openstack-neutronclient && yum clean all
