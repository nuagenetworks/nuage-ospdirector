#!/usr/bin/env bash

set -o errexit
set -o nounset
set -x

if [ "${USER}" != "stack" ]; then
    echo "ERROR: Run the script as \"stack\" user."
    exit 1
fi

source /home/stack/stackrc

echo "creating ComputeAvrs Role"
sudo openstack overcloud roles generate --roles-path /usr/share/openstack-tripleo-heat-templates/roles -o /usr/share/openstack-tripleo-heat-templates/roles/ComputeAvrs.yaml Compute
sudo sed -i -e 's/ Compute/ ComputeAvrs/g' /usr/share/openstack-tripleo-heat-templates/roles/ComputeAvrs.yaml
sudo sed -i -e "s/HostnameFormatDefault: '%stackname%-compute-%index%'/HostnameFormatDefault: '%stackname%-computeavrs-%index%'/g" /usr/share/openstack-tripleo-heat-templates/roles/ComputeAvrs.yaml
sudo sed -i -e 's/- OS::TripleO::Services::NovaCompute/- OS::TripleO::Services::NovaComputeAvrs/g'   /usr/share/openstack-tripleo-heat-templates/roles/ComputeAvrs.yaml
openstack overcloud roles generate --roles-path /usr/share/openstack-tripleo-heat-templates/roles -o /home/stack/templates/avrs-role.yaml Controller Compute ComputeAvrs

echo "Complete!! Created ComputeAvrs Role"