import logging.config
import os
import sys
import yaml
from jinja2 import Environment, FileSystemLoader


logger = logging.getLogger('')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


def generate_dockerfiles(nuage_docker_config):

    dirPath = os.path.dirname(os.path.abspath(__file__))
    
    nuage_dockerfiles = dirPath + '/nuage-dockerfiles'
    if not os.path.exists(nuage_dockerfiles):
        os.makedirs(nuage_dockerfiles)

    ENV = Environment(loader=FileSystemLoader('%s/nuage-dockerfiles-j2/' % dirPath))

    logger.debug("**Generating Nuage dockerfiles**")

    docker_images = nuage_docker_config['DockerImages'].split(' ')

    for image in docker_images:
        dockerfile_name = image + '-dockerfile'
        j2_dockerfile = dockerfile_name + '.j2'
        dockerfile = ENV.get_template(j2_dockerfile)
        with open('%s/nuage-dockerfiles/%s' %(dirPath,dockerfile_name), 'w') as dockerfile_file:
            dockerfile_file.write(dockerfile.render(nuage_docker_config=nuage_docker_config))

    nuage_repo = ENV.get_template("nuage.repo.j2")
    with open('%s/nuage-dockerfiles/nuage.repo' % dirPath, 'w') as dockerfile_file:
        dockerfile_file.write(nuage_repo.render(nuage_docker_config=nuage_docker_config))

    logger.debug("**Finished generating Nuage dockerfiles**")


def main(args):

    if len(args) < 1:
        print("**Please provide the config file as parameters and try again**")
        sys.exit(1)

    with open(sys.argv[1]) as nuage_docker_config:
        nuage_docker_config = yaml.load(nuage_docker_config)

    generate_dockerfiles(nuage_docker_config)


if __name__ == "__main__":
    main(sys.argv)
