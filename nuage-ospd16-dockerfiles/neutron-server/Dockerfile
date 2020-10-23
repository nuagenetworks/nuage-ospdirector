FROM <undercloud-doamin-name>:8787/rhosp-rhel8/openstack-neutron-server-ovn:<tag>

USER root

COPY RPM-GPG-KEY-Nuage /tmp/RPM-GPG-KEY-Nuage
COPY nuage.repo /etc/yum.repos.d/nuage.repo
RUN yum install --disablerepo "*" --enablerepo Nuage nuage-openstack-neutron nuage-openstack-neutronclient fp-vdev-remote networking-6wind -y && yum clean all


#RUN mkdir -p /opt/nuage_upgrade
#WORKDIR /opt/nuage_upgrade
#COPY nuage-openstack-upgrade-6.0.5-174.tar.gz .
#RUN tar -xzf nuage-openstack-upgrade-6.0.5-174.tar.gz
#WORKDIR /

USER neutron
