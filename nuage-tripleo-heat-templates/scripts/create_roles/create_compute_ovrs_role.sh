#!/usr/bin/env bash

set -o errexit
set -o nounset

if [ "${USER}" != "stack" ]; then
    echo "ERROR: Run the script as \"stack\" user."
    exit 1
fi

CURRENT_DIR=$(basename $(pwd))
if [ "${CURRENT_DIR}" != "create_roles" ]; then
    echo "ERROR: Run the script from create_roles directory please."
    exit 1
fi


source /home/stack/stackrc

echo "creating ComputeOvrs Role"
mkdir -p ../../roles
sudo openstack overcloud roles generate --roles-path ../../roles -o ../../roles/ComputeOvrs.yaml ComputeSriov
sudo sed -i -e 's/ ComputeSriov/ ComputeOvrs/g' ../../roles/ComputeOvrs.yaml
sudo sed -i -e 's/ Compute SR-IOV/ ComputeOvrs/g' ../../roles/ComputeOvrs.yaml
sudo sed -i -e "s/HostnameFormatDefault: '%stackname%-computesriov-%index%'/HostnameFormatDefault: '%stackname%-computeovrs-%index%'/g" ../../roles/ComputeOvrs.yaml
sudo sed -i -e '/- OS::TripleO::Services::NeutronSriovHostConfig/d'   ../../roles/ComputeOvrs.yaml
sudo sed -i -e '/- OS::TripleO::Services::NeutronSriovAgent/d'   ../../roles/ComputeOvrs.yaml

FILE=../../roles/ComputeOvrs.yaml
if [ -f "$FILE" ]; then
    echo "$FILE has been created"
else
    echo "There was some issue creating $FILE"
    exit 1
fi

echo "Complete!! Created ComputeOvrs.yaml Role files  "