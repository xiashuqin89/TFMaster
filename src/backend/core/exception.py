"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


class BaseExceptions(Exception):
    pass


class ManagerExceptions(Exception):
    msg = 'Unknown'
    status_code = '1000'

    def __init__(self, msg=None, status_code=None):
        super(ManagerExceptions, self).__init__()
        self.msg = msg if msg else self.msg
        self.status_code = status_code if status_code else self.status_code

    def __str__(self):
        return f'{self.msg}({self.status_code})'

    def __repr__(self):
        return self.__str__()


class APIRequestException(ManagerExceptions):
    msg = 'API访问缺少必要的参数'
    status_code = '5000'

    def __init__(self, url, code, msg):
        self.msg = f"{url}:{code}, {msg}"
        self.status_code = code


class AnalyzeRequestException(ManagerExceptions):
    msg = '解析异常'
    status_code = '5001'

    def __init__(self, msg):
        self.msg = f"{self.msg}:{msg}"


class StateFileGetRequestException(ManagerExceptions):
    msg = '状态文件获取异常'
    status_code = '5002'

    def __init__(self, msg):
        self.msg = f"{self.msg}:{msg}"


class ErrorRequestException(ManagerExceptions):
    msg = '访问异常'
    status_code = '5003'

    def __init__(self, msg):
        self.msg = f"{self.msg}:{msg}"


class CLITokenRequestException(ManagerExceptions):
    msg = 'CLI TOKEN 异常, 请检查TOKEN'
    status_code = '5004'

    def __init__(self, msg):
        self.msg = f"{self.msg}:{msg}"


class CLITokenExpiredException(ManagerExceptions):
    msg = 'CLI TOKEN 已经过期, 请联系管理员重新申请,申请的Token时间为:'
    status_code = '5004'

    def __init__(self, msg):
        self.msg = f"{self.msg}:{msg}"


REST_EXCEPTIONS = (
    AnalyzeRequestException, StateFileGetRequestException, APIRequestException
)
