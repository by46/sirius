from __future__ import print_function

import httplib
import json
import os
from distutils.version import LooseVersion
from itertools import chain
from itertools import imap
from etcd import Client

import requests
from fabric.api import local
from git import Repo
from simplekit import ContainerNotFound
from simplekit.docker import factory

from .setttings import DEFAULT_MATRIX_VERSION
from .setttings import DEIMOS
from .utils import group_by_2
from .utils import parse_list


def docker_dfis_prd_deploy(name, image, replicas=2, volumes=None, env=None, cmd="", hostname="sirius", servers=None):
    """deploy a docker image on dfis prd server

        will create container when if container is not exists, otherwise update container
        Example:
            sirius docker_dfis_prd_deploy:meerkat,meerkat:0.0.1,env="DEBUG\=1;PATH\=2",servers="s7dfis01;s7dfis02"

        :param name: container name
        :param image: image with tag, like: 'CentOS:7.0'
        :param replicas: container replicas
        :param volumes: like: host_file1;container_file1;host_file2;container_file2
        :param env: var=10;DEBUG=true
        :param cmd: `class`:`str`
        :param hostname:
        :param servers: s7dfis01;s7dfis02
        :return:
    """

    if servers is None:
        servers = ["s7dfis10", "s7dfis11", "s7dfis12", "s7dfis13"]
    elif servers:
        servers = parse_list(servers)

    project_name = name
    replicas = int(replicas)
    if replicas <= 0:
        raise Exception("replicas must more than 0")

    if env:
        env = parse_list(env)

    __deploy(project_name, image, replicas, volumes, env, cmd, hostname, servers, etcd_port=4007)


def docker_dev_deploy(name, image, replicas=1, volumes=None, env=None, cmd="", hostname="sirius", server=None):
    """deploy a docker image on dev server

        will create container when if container is not exists, otherwise update container
        Example:
            sirius docker_dev_deploy:meerkat,meerkat:0.0.1,env="DEBUG\=1;PATH\=2"

        :param name: container name
        :param image: image with tag, like: 'CentOS:7.0'
        :param replicas: container replicas
        :param volumes: like: host_file1;container_file1;host_file2;container_file2
        :param env: var=10;DEBUG=true
        :param cmd: `class`:`str`
        :param hostname:
        :param server:
        :return:
    """
    project_name = name
    replicas = int(replicas)
    if replicas <= 0:
        raise Exception("replicas must more than 0")

    if server is None:
        server = '10.16.78.82'

    if env:
        env = parse_list(env)
        if "ENV=gqc" in env:
            server = "10.1.24.134"

    __deploy(project_name, image, replicas, volumes, env, cmd, hostname, [server])


def docker_deploy(name, image, server=None, ports=None, volumes=None, env=None, cmd="", hostname="sirius"):
    """deploy a docker image on some server

    will create container when if container is not exists, otherwise update container
    Example:
        sirius docker_deploy:meerkat,meerkat:0.0.1,server=scdfis01,ports="3141;8080;8900;8081",env="DEBUG\=1;PATH\=2"

    :param name: container name
    :param image: image with tag, like: 'CentOS:7.0'
    :param server: which server will deploy the container, default:localhost
    :param ports: just one port, will mapping <port>:80, also accept list with public, private pairs,
           like: public1;private1;public2;private2
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
            container_volumes = [dict(hostvolume=s, containervolume=t) for s, t in group_by_2(parse_list(volumes))]
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


def docker_image_name(src='.', release=False, group=None):
    """get building docker image name
    parse matrix.json, and get image:tag

    Example:
        IMAGE_NAME=$(sirius docker_image_name | head -n 1)

    :param src: the dir which container matrix.json, default is current work directory
    :param release: generate release image name
    :param group: project group
    :return:
    """
    settings = load_settings(src)
    name = settings.get('name')

    if group:
        name = "{0}/{1}".format(group, name)

    tag = settings.get('release_tag', 'release1') if release else settings.get('tag', 'build1')

    image_name = '{name}:{tag}'.format(name=name, tag=tag)
    print(image_name)
    return image_name


def docker_build_image(workspace=None, matrix_version=None, group=None):
    """build a new image
    Example:
      sirius docker_build_image[:workspace]

    :param workspace: the source code directory, default retrieve workspace from WORKSPACE ENV variable.
    :param matrix_version: the matrix version, default is the new tag
    :param group
    :return:
    """
    if not workspace:
        workspace = os.environ.get('WORKSPACE', '.')

    if not matrix_version:
        matrix_version = os.environ.get('SIRIUS_MATRIX_VERSION')
        if not matrix_version:
            matrix_version = DEFAULT_MATRIX_VERSION
    docker_prepare_build(workspace, group)

    cmd = ('docker run --rm -v {workspace}:/home/matrix '
           '-v /var/run/docker.sock:/var/run/docker.sock docker.neg/matrix:{matrix} /usr/local/bin/matrix.sh')

    local(cmd.format(workspace=workspace, matrix=matrix_version))


def docker_new_build_no(project_slug=None):
    """get new build no

    it's used to build docker image
    Example:
        sirius docker_new_build_no:meerkat | head -n 1

    :param project_slug: project name
    :return:
    """
    url = '{0}/build/{1}'.format(DEIMOS, project_slug)
    response = requests.post(url)
    assert response.status_code == httplib.OK
    obj = response.json()
    print(obj['build_id'])
    return obj['build_id']


def docker_prepare_build(workspace=".", group=None):
    """prepare build docker image

    generate new docker image tag, and rewrite the matrix.json

    :param workspace: the matrix.json location, default './matrix.json'
    :param group
    :return:
    """
    workspace = workspace or '.'

    matrix_json = os.path.join(workspace, 'matrix.json')

    if not os.path.isfile(matrix_json):
        raise ValueError('matrix file is not exists, matrix_json={0}'.format(matrix_json))

    repo = Repo(workspace)
    commit = str(repo.head.commit.hexsha[:5])

    with open(matrix_json, 'rb') as f:
        obj = json.load(f)
        project_slug = obj['name']
        if group and not project_slug.startswith("{0}/".format(group)):
            project_slug = "{0}/{1}".format(group, project_slug)
            obj['name'] = project_slug

        build_no = docker_new_build_no(project_slug)
        tag = obj['tag']
        version = LooseVersion(tag)
        obj['tag'] = '.'.join(imap(str, chain(version.version[:3], ['build{0}'.format(build_no)])))
        obj['release_tag'] = '.'.join(
            imap(str, chain(version.version[:3], ['release{0}.{1}'.format(build_no, commit)])))

    with open(matrix_json, 'wb') as f:
        json.dump(obj, f)


def docker_release(src='.'):
    image_name = docker_image_name(src)
    release_image_name = docker_image_name(src, release=True)

    # Add new tag
    cmd = 'docker tag -f {0} docker.neg/{1}'.format(image_name, release_image_name)
    local(cmd)

    cmd = 'docker push docker.neg/{0}'.format(release_image_name)
    local(cmd)

    cmd = 'docker rmi docker.neg/{0}'.format(release_image_name)
    local(cmd)


def __deploy(project_name, image, replicas, volumes, env, cmd, hostname, servers, etcd_port=4001):
    for server in servers:
        client = factory.get(server)
        etcdClient = Client(host=server, port=etcd_port)

        for i in xrange(replicas):
            name = "{0}.{1}".format(project_name, i + 1)
            try:
                client.update_image_2(name, image)
            except ContainerNotFound:
                container_volumes = []
                if volumes:
                    container_volumes = [dict(hostvolume=s, containervolume=t) for s, t in
                                         group_by_2(parse_list(volumes))]

                code, result = client.create_container(name, image, hostname=hostname,
                                                       ports=[dict(type='tcp', privateport=8080, publicport=0)],
                                                       volumes=container_volumes, env=env,
                                                       command=cmd)
                if httplib.OK != code:
                    raise Exception("create container failure, code {0}, message: {1}".format(code, result))

            code, result = client.get_container(name, True)
            if httplib.OK != code:
                raise Exception("get container information failure, code {0}, message: {1}".format(code, result))

            port = result.NetworkSettings.Ports["8080/tcp"][0].HostPort
            etcdClient.write("/haproxy-discover/services/{0}/upstreams/{1}".format(project_name, name),
                             "{0}:{1}".format(server, port))

        upstreams = etcdClient.get("/haproxy-discover/services/{0}/upstreams".format(project_name))

        for upstream in upstreams.children:
            if isinstance(upstream.key, unicode):
                index = upstream.key[-1:]
                if index and int(index) > replicas:
                    etcdClient.delete(upstream.key)
                    client.delete_container("{0}.{1}".format(project_name, int(index)))
