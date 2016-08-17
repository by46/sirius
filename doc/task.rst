Tasks
=========================

Sirius包含了一系列可用的Task， 来完成一些常用的功能，我们按照功能来划分这些Task。

执行Task的命令格式如下：

::

	sirius task_name:param1,param2=wiki,param2=file

sirius是必选的， task_name是Task的名字, Task名字和Task的参数使用 ``:`` (冒号)分隔，多个参数之间使用 ``,`` (逗号分隔)，参数分为必选参数和可选参数，
参数可以使用 ``param_name=param_value`` 的格式，也可以使用 ``param_value`` 的格式，但是后者需要严格按照参数的顺序设置。


Docker
-----------------------------------------------

这些Task通常以 ``docker_`` 为前缀，你可以通过 ``sirius -l`` 来查看可用的任务。

docker_deploy
++++++++++++++++++++++

该task主要用于启动Docker容器， 如果Server不存在对应名称的容器，就会创建并启动该容器；
如果已经存在，就会更新该容器的镜像。

.. attention::

   底层使用的是Docker API，所以如果有环境变量，端口，卷和运行命令有更改，调用docker_deploy
   是不能更新这些信息， 需要删除容器之后，重新创建容器。这点会在将来的版本中解决。

可用参数：

- name
  必选参数，容器的名字
- image
  必选参数，启动容器的镜像名，该镜像必须要存在于 `humpback.newegg.org <http://humpback.newegg.org>`_ 中，建议包含镜像的tag。
  例如： ``meerkat:0.0.1``
- server
  可选参数， 指定部署容器的服务器的主机名，或者ip；默认值为 ``localhost`` 。
- ports
  可选参数，如果容器需要设置映射端口信息，可以通过该参数来指定映射关系；该参数相对比较复杂一些，该参数接受字符串，字符串中用 ``;`` (分号分隔)，
  以类似 ``host_port;container_port;host_port2;container_port2`` 方式设置映射关系，当前只支持tcp。默认值为空值
- volumes
  可选参数，如果容器需要设置数据卷的映射关系，可以通过该参数来指定映射关系；该参数设置和ports参数类似，
  例如``host_path;container_path;host_path2;container_path2``。默认值为空值
- env
  可选参数， 如果可以通过该参数设置容器的环境变量；环境变量由key=value,多对值之间由 ``;`` (分号)分隔，但是很重要的一点就是需要使用 ``\`` 对 ``=`` (等号)
  进行转义。例如 ``PROXY\=http://proxy`` 。默认值为空值
- cmd
  可选参数，容器启动时的命令。默认值为空值
- hostname
  可选参数， 容器的主机名，默认值为 ``sirius`` 。

例子：

::

	sirius docker_deploy:meerkat,meerkat:0.0.1,server=SCMESOS06,ports="8080;3141;8082;22",volume="/opt/meerkat/data;/opt/data",env="ENV\=prd;PATH\=1"

该命令表示在主机名为 ``SCMESOS06`` 的服务器上，以镜像 ``meerkat:0.0.1`` 启动容器，容器名为 ``meerkat`` ,
并且把scmesos06上的tcp 端口8080和tcp端口8082分别映射到容器里面的tcp端口3141和tcp端口22，同时把 ``SCMESOS06`` 上的 ``/opt/meerkat/data`` 映射到
容器内的 ``/opt/data``， 同时设置环境变量 ENV 为 prd，PATH 为 数值1。



docker_image_name
+++++++++++++++++++++

该命令通过解析matrix.json获取镜像名字， 主要用于生成镜像之后，通过该命令获取
镜像的名字和tag，用于部署，push镜像到docker.neg等操作。

建议使用方式：

::

	IMAGE_NAME=$(sirius docker_image_name | head -n 1)

可用参数：

- src
  可选参数， 指定matrix.json文件所在的目录， 默认值为当前工作目录。
- release
  可选参数， 可选值为 ``true`` 和 ``false``，如果要使用docker api启动容器，对应的镜像必须存在于docker.neg镜像私有仓库中，
  那么我们需要区分用于测试和可发布的镜像，这时就可以通过release开关来控制是生成测试还是可发布镜像的tag。
  默认值为 ``false`` 。

例如：

::

	IMAGE_NAME=$(sirius docker_image_name | head -n 1)
	# IMAGE_NAME 这个可能的值为0.0.1.build7
	IMAGE_NAME=$(sirius docker_image_name:release=true | head -n 1)
	# IMAGE_NAME 这个可能的值为0.0.1.release7.a41b5

我们通过添加第四位版本号表示构建版本，构建版本以 ``build`` 为前缀， ``7`` 为构建次数，这样0.0.1.build7就表示测试镜像；
可发布的镜像稍微有些区别，``build`` 前缀变为 ``release`` ， 并且还追加了5位git commit 号。

docker_build_image
+++++++++++++++++++++++

通过源码构建镜像

.. attention::
   由于 `Matrix <http://scmesos06/docs/by46/matrix/>`_ 现在只支持Python，所以docker_build_image也只能构建Python应用程序。

可用参数：

- workspace
  可选参数，源代码所在的目录，首先会从环境变量 ``WORKSPACE`` (为而来支持jenkins), 如果没有环境就设置当前工作目录
- matrix_version
  可选参数，指定使用matrix的版本，默认值为sirius发布时的最新版本。

例子：

::

	sirius docker_build_image

