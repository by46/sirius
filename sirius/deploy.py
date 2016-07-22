import httplib
import json

import six
from negowl import ContainerNotFound
from negowl import factory

from sirius.utils import group_by_2


def deploy(name, image, server=None, ports=None, volumes=None, env=None, cmd="", hostname="sirius"):
    """deploy image

    will create container when if container is not exists, otherwise update container

    :param name: container name
    :param image: image with tag, like: 'CentOS:7.0'
    :param server: which server will deploy the container, default:localhost
    :param ports: just one port, will mapping <port>:80, also accept list with public, private pairs, like: [public1, private1, public2, private2]
    :param volumes: like: [host_file1, container_file1, host_file2, container_file2]
    :param env: ["var=10","DEBUG=true"]
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
            ports = json.loads(ports)
            if isinstance(ports, six.integer_types):
                container_ports = [dict(type='tcp', privateport=80, publicport=ports)]
            elif isinstance(ports, list):
                container_ports = [dict(type='tcp', publicport=pub, privateport=pri) for pub, pri in group_by_2(ports)]

        container_volumes = []
        if volumes:
            volumes = json.loads(volumes)
            container_ports = [dict(containervolume=s, hostvolume=t) for s, t in group_by_2(volumes)]
        if env:
            env = json.loads(env)

        code, result = client.create_container(name, image, hostname=hostname, ports=container_ports,
                                               volumes=container_volumes, env=env,
                                               command=cmd)
        if httplib.OK != code:
            raise Exception("create container failure, code {0}, message: {1}".format(code, result))
