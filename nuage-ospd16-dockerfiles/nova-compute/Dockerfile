FROM <undercloud-doamin-name>:8787/rhosp-rhel8/nova-compute:<tag>

USER root

COPY RPM-GPG-KEY-Nuage /tmp/RPM-GPG-KEY-Nuage
COPY nuage.repo /etc/yum.repos.d/nuage.repo
RUN yum install --disablerepo "*" --enablerepo Nuage fp-vdev-remote os-vif-6wind-plugin -y && yum clean all

USER nova
