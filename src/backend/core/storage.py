"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json
import datetime

import requests
from requests.auth import HTTPBasicAuth

from setting.config import options
from .exception import APIRequestException, StateFileGetRequestException


def push_file(prefix, payload):
    """
    推送文件
    :param prefix:
    :param payload:
    :return:
    """
    url = f"{options['STORAGE_URL']}/{prefix}"
    headers = {
        'Content-Type': 'text/plain',
    }
    operator = options['STORAGE_OPERATOR']
    auth_token = options['STORAGE_CODE']
    res = requests.request("PUT",
                           url,
                           headers=headers,
                           data=payload,
                           auth=HTTPBasicAuth(operator, auth_token))
    if res.status_code != 200:
        raise APIRequestException(url, res.status_code, res.text)
    res_json = json.loads(res.text)
    if res_json.get('error'):
        raise APIRequestException(url, res_json.get("code"), res.text)
    if res_json.get('result') is False:
        raise APIRequestException(url, res_json.get("code"), res.text)
    return res_json["data"]


def pull_file(prefix):
    """
    下载文件
    :param prefix:
    :param auth_token:
    :param operator:
    :return:
    """
    url = f"{options['STORAGE_URL']}/{prefix}"
    headers = {
        'Content-Type': 'text/plain',
    }
    operator = options['STORAGE_OPERATOR']
    auth_token = options['STORAGE_CODE']
    res = requests.request("GET", url, headers=headers, auth=HTTPBasicAuth(
        operator, auth_token
    ))
    if res.status_code != 200:
        res_json = json.loads(res.text)
        raise StateFileGetRequestException(res_json["message"])
    return res.text


def delete_file(prefix):
    """
    删除文件
    :param prefix:
    :param auth_token:
    :param operator:
    :return:
    """
    url = f"{options['STORAGE_URL']}/{prefix}"
    headers = {
        'Content-Type': 'text/plain',
    }
    operator = options['STORAGE_OPERATOR']
    auth_token = options['STORAGE_CODE']
    res = requests.request("DELETE", url, headers=headers, auth=HTTPBasicAuth(
        operator, auth_token
    ))
    return res.text


class StateMng(object):
    def __init__(self, operator, biz_id):
        self.lock_file = "state.lock"
        self.state_file = "state-list.txt"
        self.operator = operator
        self.biz_id = biz_id

    def __enter__(self):
        # 获得锁
        delete_file(prefix=self.init_prefix(self.lock_file))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        push_file(prefix=self.init_prefix(self.lock_file),
                  payload=str(datetime.datetime.now()))
        if exc_type:
            return False

    def init_prefix(self, obj_name):
        return ""f'tfmaster/{self.operator}/{str(self.biz_id)}/{obj_name}'

    def get_state_list(self):
        try:
            state_list_content = pull_file(self.init_prefix(self.state_file)).split("\n")
        except:
            state_list_content = []
        return state_list_content

    def push(self, obj_name, content, force_replace=False):
        state_list_content = self.get_state_list()
        if force_replace:
            delete_file(self.init_prefix(
                obj_name
            ))
        push_file(self.init_prefix(
            obj_name
        ), content)

        if obj_name not in state_list_content:
            state_list_content.append(obj_name)
            delete_file(self.init_prefix(
                self.state_file
            ))
            push_file(self.init_prefix(
                self.state_file
            ), "\n".join(state_list_content))

    def pull(self, obj_name):
        return pull_file(
            self.init_prefix(obj_name)
        )

    def pull_all(self):
        state_list_content = self.get_state_list()
        for state in state_list_content:
            yield self.pull(state)


def init_prefix(operator, biz_id, obj_name):
    return ""f'tfmaster/{operator}/{str(biz_id)}/{obj_name}'
