# !/usr/bin/python
# Copyright 2019 NOKIA
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


from jinja2 import Environment, FileSystemLoader
import argparse
import os
import sys
import subprocess
import yaml
import logging

# Logging
LOGFILE="nuage_containers_pull.log"
logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)
handler = logging.FileHandler(LOGFILE)
handler.setFormatter(formatter)
logger.addHandler(handler)


#####
# Check if the provided path to the file exists
#####

def file_exists(filename):
    if os.path.isfile(filename):
        return True
    else:
        logger.error("%s is not present in the location of this "
                     "script" % filename)
        sys.exit(1)


#####
# Generates nauge_local_registry_images.yaml, with Nuage conatiner
# names and push destination
#

def generate_local_registry_nuage_images(nuage_config):
    dirPath = os.path.dirname(os.path.abspath(__file__))
    ENV = Environment(loader=FileSystemLoader('%s/' % dirPath))
    nuage_images_file_name = 'nuage_local_registry_images.yaml'
    j2_nuage_images_file_name = nuage_images_file_name + '.j2'
    file_exists(dirPath + '/' + j2_nuage_images_file_name)
    nuage_images_file = ENV.get_template(j2_nuage_images_file_name)
    logger.info("Rendering nuage_local_registry_images.yaml file")
    with open('%s/%s' % (dirPath, nuage_images_file_name),
              'w') as local_images_file:
        local_images_file.write(
            nuage_images_file.render(nuage_config=nuage_config))
    logger.info("Rendering nuage_local_registry_images.yaml is "
                "completed")
    return nuage_images_file_name


#####
# Generates nuage_overcloud_images.yaml with Nuage container names
# that need to be pulld by overcloud nodes during deployment
#####

def generate_nuage_overcloud_images(nuage_config):
    dirPath = os.path.dirname(os.path.abspath(__file__))
    envPath = dirPath.split('scripts')[0] + 'environments'
    if not os.path.isdir(envPath):
        logger.error("%s directory is not present " % envPath)
        sys.exit(1)
    ENV = Environment(loader=FileSystemLoader('%s/' % dirPath))
    nuage_overcloud_images_file_name = 'nuage_overcloud_images.yaml'
    j2_nuage_overcloud_images_file_name = \
        nuage_overcloud_images_file_name + '.j2'
    file_exists(dirPath + '/' + j2_nuage_overcloud_images_file_name)
    nuage_overcloudimages_file = ENV.get_template(
        j2_nuage_overcloud_images_file_name)
    logger.info("Rendering nuage_overcloud_images.yaml file")
    with open('%s/%s' % (envPath, nuage_overcloud_images_file_name),
              'w') as overcloud_images_file:
        overcloud_images_file.write(nuage_overcloudimages_file.render(
            nuage_config=nuage_config))
    logger.info("Redering nuage_overcloud_images.yaml is completed")


#####
# This function is responsible to pull Nuage container images from
# Red Hat Regsitry, retag them all with registry as local registry ,
# push the retagged images to local regstiry and once pushing is done,
# remove them all from undercloud machine.
#####

def pull_retag_push_nuage_images(config_file):
    upload_cmd = 'openstack overcloud container image upload   ' \
                 '--config-file  ' + config_file + ' --verbose'
    logger.info("Pulling the Nuage Container images to Local registry")
    subprocess.call(upload_cmd, shell=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nuage-config", dest="nuage_config",
                        type=str, required=True,
                        help="path to nuage_container_config.yaml")
    args = parser.parse_args()

    with open(args.nuage_config) as nuage_config:
        nuage_config = yaml.load(nuage_config)

    config_file = generate_local_registry_nuage_images(nuage_config)
    generate_nuage_overcloud_images(nuage_config)
    pull_retag_push_nuage_images(config_file)


if __name__ == "__main__":
    main()
