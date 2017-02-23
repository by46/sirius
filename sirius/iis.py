from etcd import Client

import subprocess

ADD_APP = 'appcmd add app /site.name:"DAE" /path:/{0} /physicalPath:"{1}"'
UPDATE_APP = 'appcmd set app /app.name:"DAE/{0}" /applicationPool:"ASP.NET v4.0 Classic"'


def iis_deploy(name, path, server=None, etcd_port=4001):

    if server is None:
        server = '10.16.78.82'

    for command in [ADD_APP.format(name, path), UPDATE_APP.format(name)]:
        if subprocess.call(command, shell=True) not in (0, 183):
            raise Exception("appcmd faild {0}".format(command))

    etcd_client = Client(host=server, port=etcd_port)
    etcd_client.write("/haproxy-discover/services/{0}/upstreams/{0}.1".format(name), "scmisdae01:8090")

