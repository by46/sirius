
import httplib
import json
import os.path

from negowl import ContainerNotFound
from negowl import factory

from sirius.utils import group_by_2
from sirius.utils import parse_list


def deploy(name, image, server=None, ports=None, volumes=None, env=None, cmd="", hostname="sirius"):
    """deploy image

    will create container when if container is not exists, otherwise update container
    Example:
        fab deploy:meerkat,meerkat:0.0.1,server=scdfis01,ports="3141;8080;8900;8081",env="DEBUG\=1;PATH\=2"

    :param name: container name
    :param image: image with tag, like: 'CentOS:7.0'
    :param server: which server will deploy the container, default:localhost
    :param ports: just one port, will mapping <port>:80, also accept list with public, private pairs, like: public1;private1;public2;private2
    :param volumes: like: host_file1;container_file1;host_file2;container_file2
    :param env: var=10;DEBUG=true
    :param cmd: `class`:`str`
    :param hostname:
    :return:
    """
    if server is None:
        server = 'localhost'
    client = factory.get(server)
    try:
        client.update_image_2(name, image)
    except ContainerNotFound:
        container_ports = []
        if ports:
            ports = parse_list(ports)
            if len(ports) == 1:
                container_ports = [dict(type='tcp', privateport=80, publicport=int(ports[0]))]
            else:
                container_ports = [dict(type='tcp', publicport=int(pub), privateport=int(pri)) for pub, pri in
                                   group_by_2(ports)]

        container_volumes = []
        if volumes:
            volumes = json.loads(volumes)
            container_ports = [dict(containervolume=s, hostvolume=t) for s, t in group_by_2(parse_list(volumes))]
        if env:
            env = parse_list(env)

        code, result = client.create_container(name, image, hostname=hostname, ports=container_ports,
                                               volumes=container_volumes, env=env,
                                               command=cmd)
        if httplib.OK != code:
            raise Exception("create container failure, code {0}, message: {1}".format(code, result))


def load_settings(src):
    full_path = os.path.join(src, 'matrix.json')
    with open(full_path, 'rb') as f:
        return json.load(f)


def image_name(src='.'):
    """get build image name
    parse matrix.json, and get image:tag

    Example:
        IMAGE_NAME=$(sirius image_name | head -n 1)

    :param src: the dir which container matrix.json, default is current work directory
    :return:
    """
    settings = load_settings(src)
    print '{name}:{tag}'.format(name=settings.get('name'), tag=settings.get('tag', 'latest'))


def build_image():
    """build a new iamge

    :return:
    """
    from fabric.api import local
    local('docker run --rm -v ${WORKSPACE}:/home/matrix -v /usr/bin/docker:/usr/bin/docker -v /var/run/docker.sock:/var/run/docker.sock docker.neg/matrix:0.0.3 /usr/local/bin/matrix.sh')

