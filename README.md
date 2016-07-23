# Sirius
Sirius 是用于Jenkins持续集成的常用功能集合，便于简单、快速的使用Jenkins实践持续集成。

## Dependencies
- Linux System
- Python 2.7+
- Docker 1.8.3 (某些功能依赖)

## Quick Start
### Installation
sirius可以使用pip来快速安装，执行以下命令来快速安装sirius:

```shell
sudo pip --trusted-host scmesos06 install -i http://scmesos06:3141/simple sirius

```

### Usage
我们在底层使用了[Fabric](http://docs.fabfile.org/en/1.11/index.html#)，所以我们借鉴Fabric的Task的概念。
所以你可以执行下面有哪些可以用的Task：

```shell
sirius -l
```

执行完了之后， 你可以得到如下结果：

```shell
Available commands:

    docker_deploy      deploy a docker image on some server
    docker_image_name  get building docker image name
    usage              help information
    version            version information
        
```

如果你想查看Task的详细信息，可以执行以下命令查看：
```shell
sirius -d docker_deploy
```

那么我们就会得到docker_deploy 任务的详细信息:

```shell
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

```