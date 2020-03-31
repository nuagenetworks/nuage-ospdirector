#!/bin/bash

set -e

# Set default values for the following variables if they're not already set.
NUAGE_OSPD_RELEASE="${NUAGE_OSPD_RELEASE:-16}"
NUAGE_PROJECT="${NUAGE_PROJECT:-0}"
NUAGE_BUILD_RELEASE="${NUAGE_BUILD_RELEASE:-0}"

# $GIT_DIR should be the base directory of the git tree.  Since that's where the
# script is, we can locate the git tree based on that.
GIT_DIR=$(dirname $0)
WORKSPACE=$(echo $PWD)

# Create the RPM directories in the workspace
mkdir -p $WORKSPACE/rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

# tar the sources
tar -czf $WORKSPACE/rpmbuild/SOURCES/nuage-tripleo-heat-templates.tar.gz -C $GIT_DIR nuage-tripleo-heat-templates

# create the spec file from the spec.in
version="${NUAGE_OSPD_RELEASE}.${NUAGE_PROJECT}"
sed "s/@VERSION@/$version/" $GIT_DIR/nuage-tripleo-heat-templates.spec.in > $WORKSPACE/rpmbuild/SPECS/nuage-tripleo-heat-templates.spec

# build the rpm
cd $WORKSPACE/rpmbuild
rpmbuild --define "_topdir $WORKSPACE/rpmbuild" -ba SPECS/nuage-tripleo-heat-templates.spec --define "release $NUAGE_BUILD_RELEASE" --define "dist .el8"
