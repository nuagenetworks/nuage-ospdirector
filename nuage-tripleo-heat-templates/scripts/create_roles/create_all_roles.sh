#!/usr/bin/env bash
# TODO(vandewat|Oguz|Steven) Instead of this find/replace magic let's parse yaml / modify / dump

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

# Create ComputeOvrs role
echo "creating ComputeOvrs Role"
mkdir -p ../../roles
openstack overcloud roles generate --roles-path ../../roles -o ../../roles/ComputeOvrs.yaml ComputeSriov
sed -i -e 's/ ComputeSriov/ ComputeOvrs/g' ../../roles/ComputeOvrs.yaml
sed -i -e 's/ Compute SR-IOV/ ComputeOvrs/g' ../../roles/ComputeOvrs.yaml
sed -i -e "s/HostnameFormatDefault: '%stackname%-computesriov-%index%'/HostnameFormatDefault: '%stackname%-computeovrs-%index%'/g" ../../roles/ComputeOvrs.yaml
sed -i -e '/- OS::TripleO::Services::NeutronSriovHostConfig/d'   ../../roles/ComputeOvrs.yaml
sed -i -e '/- OS::TripleO::Services::NeutronSriovAgent/d'   ../../roles/ComputeOvrs.yaml

FILE=../../roles/ComputeOvrs.yaml
if [ -f "$FILE" ]; then
    echo "$FILE has been created"
else
    echo "There was some issue creating $FILE"
    exit 1
fi

echo "Complete!! Created ComputeOvrs.yaml Role files  "

# Create ComputeAvrs role
echo "creating ComputeAvrs Role"
mkdir -p ../../roles
openstack overcloud roles generate --roles-path ../../roles -o ../../roles/ComputeAvrs.yaml Compute
sed -i -e 's/ Compute/ ComputeAvrs/g' ../../roles/ComputeAvrs.yaml
sed -i -e "s/HostnameFormatDefault: '%stackname%-novacompute-%index%'/HostnameFormatDefault: '%stackname%-novacomputeavrs-%index%'/g" ../../roles/ComputeAvrs.yaml
sed -i -e 's/- OS::TripleO::Services::NovaCompute/- OS::TripleO::Services::NovaComputeAvrs/g'   ../../roles/ComputeAvrs.yaml
sed -i -e "s/- OS::TripleO::Services::ComputeNeutronCorePlugin/- OS::TripleO::Services::ComputeNeutronCorePluginNuage/g"   ../../roles/ComputeAvrs.yaml
echo "    - OS::TripleO::Services::ComputeNeutronFastpathAgent" >> ../../roles/ComputeAvrs.yaml

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
    openstack overcloud roles generate --roles-path ../../roles -o ../../roles/${role}.yaml Compute
    sed -i -e "s/ Compute/ ${role}/g" ../../roles/${role}.yaml
    sed -i -e "s/HostnameFormatDefault: '%stackname%-novacompute-%index%'/HostnameFormatDefault: '%stackname%-nova${role,,}-%index%'/g" ../../roles/${role}.yaml
    sed -i -e "s/- OS::TripleO::Services::NovaCompute/- OS::TripleO::Services::NovaComputeAvrs/g"   ../../roles/${role}.yaml
    sed -i -e "s/- OS::TripleO::Services::ComputeNeutronCorePlugin/- OS::TripleO::Services::ComputeNeutronCorePluginNuage/g"   ../../roles/${role}.yaml
    echo "    - OS::TripleO::Services::ComputeNeutronFastpathAgent" >> ../../roles/${role}.yaml
    FILE=../../roles/${role}.yaml
    if [ -f "$FILE" ]; then
        echo "$FILE has been created"
    else
        echo "There was some issue creating $FILE"
        exit 1
    fi
done

echo "Complete!! Created  ${roles[*]} Roles files "