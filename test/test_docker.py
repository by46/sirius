import httplib
import os.path
import unittest

import requests
from mock import call
from mock import mock_open
from mock import patch
from simplekit import ContainerNotFound
from simplekit.docker import Docker

from sirius.docker import docker_build_image
from sirius.docker import docker_deploy
from sirius.docker import docker_image_name
from sirius.docker import docker_release


class DockerTestCase(unittest.TestCase):
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
