Quick Start
======================

Sirius 是用于Jenkins持续集成的常用功能集合，便于简单、快速的使用Jenkins实践持续集成。

Dependencies
---------------------------------------------

- Python 2.7+
- Docker 1.8.3 (某些功能依赖)

Installation
----------------------------------------------
sirius可以使用pip来快速安装，执行以下命令:

::

  pip --trusted-host scmesos06 install -i http://scmesos06/simple sirius

Usage
-----------------------------------------

我们在底层使用了 `Fabric <http://docs.fabfile.org/en/1.11/index.html>`_，所以我们借鉴Fabric的Task的概念。

Available Task
++++++++++++++++++++++

所以你可以执行下面有哪些可以用的Task：

::

	sirius -l
	# or
	sirius --list


执行完了之后， 你可以得到如下结果：

::

	Available commands:

		docker_deploy      deploy a docker image on some server
		docker_image_name  get building docker image name
		usage              help information
		version            version information


Task Description
+++++++++++++++++++++++++

如果你想查看Task的详细信息，可以执行以下命令查看：

::

	sirius -d docker_deploy
	# or
	sirius --display docker_deploy

那么我们就会得到docker_deploy 任务的详细信息:

::

 Displaying detailed information for task 'docker_deploy':

    deploy a docker image on some server

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

    Arguments: name, image, server=None, ports=None, volumes=None, env=None, cmd='', hostname='sirius'

Execute Task
++++++++++++++++++++++

我们得到了Task的详细信息之后，我们就可以根据描述信息来尝试使用， sirius采用这样 ``sirius COMMAND:param1,param2,param3=value3`` 的格式执行。
例如我们我们要执行部署工作，我们就可以执行如下命令：

::

	sirius docker_deploy:container_name,docker.neg/meerkat:0.0.1,scdfis00, ports=3141;8080

通过这个命令我们就在scdfis00的服务器上使用 ``docker.neg/meerka:0.0.1`` 的镜像启动了一个叫做container_name的容器，
并把scdfis00 上的3141 tcp端口映射到了容器内部的8080tcp端口。当然还可以设置容器的卷、环境变量等，具体设置方式可以参照任务描述信息。

但是有一点必须注意的是， scdfis00上必须安装 `dockerapi <http://trgit2/backend_framework/docker-manage-api>`_ 。