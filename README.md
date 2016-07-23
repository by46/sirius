# Sirius
Sirius 是用于Jenkins持续集成的常用功能集合，用于简单，快速的使用Jenkins实践持续集成。

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
Usage Example:

    sirius -l
        print list of possible commands and exit
    sirius -d NAME
        print detailed info about command NAME
    sirius COMMAND
        execute COMMAND
        
```
