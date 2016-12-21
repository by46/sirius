import httplib
import os.path
import unittest

import requests
from etcd import Client
from etcd import EtcdResult
from mock import call
from mock import mock_open
from mock import patch
from simplekit import ContainerNotFound
from simplekit import objson
from simplekit.docker import Docker

from sirius.docker import docker_build_image
from sirius.docker import docker_deploy
from sirius.docker import docker_image_name
from sirius.docker import docker_release
from sirius.docker import docker_dev_deploy
from sirius.docker import docker_dfis_prd_deploy


class DockerTestCase(unittest.TestCase):

    def test_dfis_prd_deploy_docker_replicas_exception(self):
        self.assertRaises(Exception, docker_dfis_prd_deploy, "", "", 0)


    @patch.object(Docker,'update_image_2')
    @patch.object(Docker,'get_container')
    @patch.object(Client,'write')
    @patch.object(Client,'get')
    def test_dfis_prd_deploy_docker(self,get,write,get_container,update_image):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        get.return_value = EtcdResult(node=[])
        get_container.return_value = 200,objson.loads('{"NetworkSettings":{"Ports":{"8080/tcp":[{"HostPort":"80"}]}}}')
        docker_dfis_prd_deploy(name, image,replicas=1,env="ENV=gqc",servers='scmesos02')
        write.assert_called_with('/haproxy-discover/services/StubDemo/upstreams/StubDemo.1', 'scmesos02:80')
        update_image.assert_called_with('StubDemo.1', image)

    def test_dev_deploy_docker_replicas_exception(self):
        self.assertRaises(Exception, docker_dev_deploy, "", "", 0)

    @patch.object(Docker,'update_image_2')
    @patch.object(Docker,'get_container')
    @patch.object(Docker, 'delete_container')
    @patch.object(Client,'write')
    @patch.object(Client,'get')
    @patch.object(Client, 'delete')
    def test_dev_deploy_docker_scale(self,delete,get,write,delete_container,get_container,update_image):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        get.return_value = EtcdResult(node={u'nodes':[{u'key':u'/upstreams/StubDemo.1'},{u'key':u'/upstreams/StubDemo.2'}],u'dir':True})
        get_container.return_value = 200,objson.loads('{"NetworkSettings":{"Ports":{"8080/tcp":[{"HostPort":"80"}]}}}')
        docker_dev_deploy(name, image)
        delete.assert_called_with('/upstreams/StubDemo.2')
        delete_container.assert_called_with('StubDemo.2')
        write.assert_called_with('/haproxy-discover/services/StubDemo/upstreams/StubDemo.1', 'scmesos02:80')
        update_image.assert_called_with('StubDemo.1', image)

    @patch.object(Docker,'update_image_2')
    @patch.object(Docker,'get_container')
    @patch.object(Client,'write')
    @patch.object(Client,'get')
    def test_dev_deploy_docker(self,get,write,get_container,update_image):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        get.return_value = EtcdResult(node=[])
        get_container.return_value = 200,objson.loads('{"NetworkSettings":{"Ports":{"8080/tcp":[{"HostPort":"80"}]}}}')
        docker_dev_deploy(name, image)
        write.assert_called_with('/haproxy-discover/services/StubDemo/upstreams/StubDemo.1', 'scmesos02:80')
        update_image.assert_called_with('StubDemo.1', image)

    @patch.object(Docker, 'update_image_2')
    @patch.object(Docker, 'get_container')
    @patch.object(Client, 'write')
    @patch.object(Client,'get')
    def test_dev_deploy_docker_gqc(self, get, write, get_container, update_image):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        get.return_value = EtcdResult(node=[])
        get_container.return_value = 200, objson.loads('{"NetworkSettings":{"Ports":{"8080/tcp":[{"HostPort":"80"}]}}}')
        docker_dev_deploy(name, image,env="ENV=gqc")
        write.assert_called_with('/haproxy-discover/services/StubDemo/upstreams/StubDemo.1', '10.1.24.134:80')
        update_image.assert_called_with('StubDemo.1', image)

    @patch.object(Docker,'update_image_2')
    @patch.object(Docker,'get_container')
    def test_dev_deploy_docker_get_container_faild(self,get_container,update_image):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        get_container.return_value = 500,None
        self.assertRaises(Exception, docker_dev_deploy, name, image)
        update_image.assert_called_with('StubDemo.1', image)

    @patch.object(Docker, 'create_container')
    @patch.object(Docker, 'update_image_2')
    @patch.object(Docker, 'get_container')
    @patch.object(Client, 'write')
    @patch.object(Client,'get')
    def test_dev_deploy_docker_create_container(self,get,write,get_container, update_image,create_container):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        volumes = "host_file1;container_file1;host_file2;container_file2"
        get.return_value = EtcdResult(node=[])
        update_image.side_effect = ContainerNotFound
        get_container.return_value = 200, objson.loads('{"NetworkSettings":{"Ports":{"8080/tcp":[{"HostPort":"80"}]}}}')
        create_container.return_value = 200,None
        docker_dev_deploy(name, image,volumes=volumes)
        write.assert_called_with('/haproxy-discover/services/StubDemo/upstreams/StubDemo.1', 'scmesos02:80')
        update_image.assert_called_with('StubDemo.1', image)
        create_container.assert_called_with("StubDemo.1", image, hostname='sirius', command='',
                                            env=None,ports=[{'publicport':0,'type':'tcp','privateport':8080}],
                                            volumes=[{'containervolume': 'container_file1', 'hostvolume': 'host_file1'},
                                                     {'containervolume': 'container_file2',
                                                      'hostvolume': 'host_file2'}])

    @patch.object(Docker, 'create_container')
    @patch.object(Docker, 'update_image_2')
    def test_dev_deploy_docker_create_container_faild(self, update_image,create_container):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        volumes = "host_file1;container_file1;host_file2;container_file2"
        update_image.side_effect = ContainerNotFound
        create_container.return_value = (httplib.INTERNAL_SERVER_ERROR, None)
        self.assertRaises(Exception, docker_dev_deploy, name, image, volumes=volumes)
        update_image.assert_called_with("StubDemo.1", image)
        create_container.assert_called_with("StubDemo.1", image, hostname='sirius', command='',
                                            env=None,ports=[{'publicport':0,'type':'tcp','privateport':8080}],
                                            volumes=[{'containervolume': 'container_file1', 'hostvolume': 'host_file1'},
                                                     {'containervolume': 'container_file2',
                                                      'hostvolume': 'host_file2'}])

    @patch.object(Docker, 'update_image_2')
    def test_deploy_docker(self, update_image):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        docker_deploy(name, image)
        update_image.assert_called_with(name, image)

    @patch.object(Docker, 'create_container')
    @patch.object(Docker, 'update_image_2')
    def test_deploy_docker_exception(self, update_image, create_container):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        ports = "3141;8080"
        volumes = "host_file1;container_file1;host_file2;container_file2"
        env = "DEBUG=1"
        cmd = "python run.py"
        update_image.side_effect = ContainerNotFound
        create_container.return_value = (httplib.INTERNAL_SERVER_ERROR, None)

        self.assertRaises(Exception, docker_deploy, name, image, ports=ports, volumes=volumes, env=env, cmd=cmd)
        update_image.assert_called_with(name, image)
        create_container.assert_called_with(name, image, hostname='sirius',
                                            ports=[{'publicport': 3141, 'type': 'tcp', 'privateport': 8080}],
                                            volumes=[{'containervolume': 'container_file1', 'hostvolume': 'host_file1'},
                                                     {'containervolume': 'container_file2',
                                                      'hostvolume': 'host_file2'}],
                                            env=[env],
                                            command=cmd)

    @patch.object(Docker, 'create_container')
    @patch.object(Docker, 'update_image_2', )
    def test_docker_deploy_default_port(self, update_image, create_container):
        name = 'StubDemo'
        image = 'docker.neg/demo'
        ports = "3141"

        update_image.side_effect = ContainerNotFound
        create_container.return_value = (httplib.OK, None)
        docker_deploy(name, image, ports=ports)

        update_image.assert_called_with(name, image)
        create_container.assert_called_with(name, image,
                                            ports=[{'publicport': 3141, 'type': 'tcp', 'privateport': 80}],
                                            command='',
                                            hostname='sirius',
                                            volumes=[],
                                            env=None)

    @patch('sirius.docker.print')
    @patch('sirius.docker.open', mock_open(read_data='{"name":"demo","tag":"build20"}'))
    def test_docker_image_name(self, mock_print_function):
        self.assertEqual("demo:build20", docker_image_name())
        mock_print_function.assert_called_with('demo:build20')

    @patch('sirius.docker.print')
    @patch.object(requests, 'post')
    @patch('sirius.docker.open', mock_open(read_data='{"name":"demo","tag":"build20"}'))
    @patch('sirius.docker.Repo')
    @patch.object(os.path, 'isfile')
    @patch('sirius.docker.local')
    def test_docker_build_image(self, local, isfile, repo_class, post, mock_print_function):
        repo_class.return_value.head.commit.hexsha = "11223344556"
        isfile.return_value = True
        post.return_value.status_code = httplib.OK
        post.return_value.json.return_value = dict(build_id=1)

        # Assertion

        docker_build_image(workspace='.')
        local.assert_called_with('docker run --rm -v .:/home/matrix '
                                 '-v /usr/bin/docker:/usr/bin/docker '
                                 '-v /var/run/docker.sock:/var/run/docker.sock '
                                 'docker.neg/matrix:0.0.4 /usr/local/bin/matrix.sh')
        isfile.assert_called_with(os.path.join('.', 'matrix.json'))
        mock_print_function.assert_called_with(1)

    @patch('sirius.docker.local')
    @patch('sirius.docker.docker_image_name')
    def test_docker_release(self, image_name, local):
        image_name.return_value = 'build1'
        docker_release()

        # Assertion
        self.assertListEqual([call('.'), call('.', release=True)], image_name.mock_calls)
        self.assertListEqual([call('docker tag -f build1 docker.neg/build1'),
                              call('docker push docker.neg/build1'),
                              call('docker rmi docker.neg/build1')],
                             local.mock_calls)
