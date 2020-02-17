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

# Create ComputeAvrs role
echo "creating ComputeAvrs Role"
mkdir -p ../../roles
sudo openstack overcloud roles generate --roles-path ../../roles -o ../../roles/ComputeAvrs.yaml Compute
sudo sed -i -e 's/ Compute/ ComputeAvrs/g' ../../roles/ComputeAvrs.yaml
sudo sed -i -e "s/HostnameFormatDefault: '%stackname%-compute-%index%'/HostnameFormatDefault: '%stackname%-computeavrs-%index%'/g" ../../roles/ComputeAvrs.yaml
sudo sed -i -e 's/- OS::TripleO::Services::NovaCompute/- OS::TripleO::Services::NovaComputeAvrs/g'   ../../roles/ComputeAvrs.yaml

FILE=../../roles/ComputeAvrs.yaml
if [ -f "$FILE" ]; then
    echo "$FILE has been created"
else
    echo "There was some issue creating $FILE"
    exit 1
fi

echo "Complete!! Created ComputeAvrs.yaml Role files  "


# Create ComputeAvrsSingle and ComputeAvrsDual roles
roles=(ComputeAvrsSingle ComputeAvrsDual)
echo "creating ${roles[*]} Role"

mkdir -p ../../roles
for role in "${roles[@]}"; do
    sudo openstack overcloud roles generate --roles-path ../../roles -o ../../roles/${role}.yaml Compute
    sudo sed -i -e "s/ Compute/ ${role}/g" ../../roles/${role}.yaml
    sudo sed -i -e "s/HostnameFormatDefault: '%stackname%-compute-%index%'/HostnameFormatDefault: '%stackname%-${role,,}-%index%'/g" ../../roles/${role}.yaml
    sudo sed -i -e "s/- OS::TripleO::Services::NovaCompute/- OS::TripleO::Services::NovaComputeAvrs/g"   ../../roles/${role}.yaml
    FILE=../../roles/${role}.yaml
    if [ -f "$FILE" ]; then
        echo "$FILE has been created"
    else
        echo "There was some issue creating $FILE"
        exit 1
    fi
done

echo "Complete!! Created  ${roles[*]} Roles files "


# Create ComputeOvrs role
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