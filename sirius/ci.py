from __future__ import print_function

import json
import requests
import os
import base64
import time

def get_config(cloud_data, job_name, out_put=None):
    """get ci config from cloud_data

        :param cloud_data: cloud data url
        :param job_name: job name, like: 'Analysis'
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
        jobs = json.loads(res.content)['jobs']
        for job in jobs:
            if job_name in job:
                with open(os.path.join(out_put, job_name.lower() + ".sh"), mode='w') as f:
                    f.write(job[job_name])