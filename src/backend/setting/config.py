"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os
import importlib
import sys

current_path = os.getcwd()
package_path = os.path.dirname(__file__)
sys.path.append(package_path)
pwd_path = os.getcwd()


class Options(dict):
    def set_options(self, key, value):
        self[key] = value

    def __getattr__(self, item):
        return self[item]


options = Options()


def copy_options(o):
    new_options = Options()
    for k, v in o.items():
        new_options.set_options(k, v)

    return new_options


def load_config():
    # 执行环境
    options.set_options("RUN_ENV", os.environ.get('RUN_ENV') or "prod")
    options.set_options("APIGW_PUBLIC_KEY", os.environ.get('APIGW_PUBLIC_KEY'))


def load_config_from_env():
    env_dist = os.environ
    for key, _ in options.items():
        if key in env_dist:
            options[key] = env_dist[key]


def load_pkg_config(pkg_name):
    pkg_module = importlib.import_module(pkg_name, package_path)
    for _c in dir(pkg_module):
        if _c.startswith("_") is False:
            options.set_options(_c, getattr(pkg_module, _c))


def load_target_env():
    try:
        load_pkg_config(options.RUN_ENV)
    except ModuleNotFoundError:
        pass


# 加载顺序：默认、指定环境、环境变量
load_config()
load_config_from_env()
load_target_env()


