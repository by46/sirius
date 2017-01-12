from __future__ import print_function

import json
import requests
import os
import base64
import time


def get_config(cloud_data, out_put=None):
    """get ci config from cloud_data

        :param cloud_data: cloud data url
        :param out_put: ci file dir
        :return:
    """

    if out_put is None:
        out_put = "ci"

    if not os.path.exists(out_put):
        os.mkdir(out_put)

    cloud_data = base64.b64decode(cloud_data)

    res = requests.get("{0}?dt={1}".format(cloud_data, time.time()))

    if res.status_code == 200:
        jobs = json.loads(res.content)['jobs_detail']
        for job in jobs:
            name = job.keys()[0]
            with open(os.path.join(out_put, name.lower() + ".sh"), mode='w') as f:
                f.write(job[name])


def update_config(cloud_data, docker_release_image=None):
    """get ci config from cloud_data

        :param cloud_data: cloud data url
        :param docker_release_image: docker release image
        :return:
    """

    if docker_release_image:
        cloud_data = base64.b64decode(cloud_data)
        index = cloud_data.rfind("/")
        url = cloud_data[:index]
        key = cloud_data[index + 1:]
        res = requests.put(url, headers={'Content-Type': 'application/json'}, json={
            'key': key,
            'docker_release_image': docker_release_image
        })
        if res.status_code != 202:
            raise Exception("call cloud data {0}, update {1} faild. {2}".format(url, key, res.content))

