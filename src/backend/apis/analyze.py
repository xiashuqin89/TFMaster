"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from fastapi import File, UploadFile, Request
from core.utils import return_raw_data
from core.parser import parser, FilterParams, QueryParams
from fastapi import APIRouter
from pydantic import BaseModel, Field as PYField
from core.storage import StateMng
from core.cache import global_cache

router = APIRouter()


@global_cache
def get_content(username, session_key):
    content_list = []
    with StateMng(username, session_key) as sm:
        for c in sm.pull_all():
            content_list.append(c)
        # if len(content_list) == 0:
        #     content_list.append(sm.pull("latest.json"))
    return content_list


class AnalyzeModel(BaseModel):
    filter: FilterParams = PYField(default=None)
    query: QueryParams = PYField(default=None)


@router.post("/upload/{username}/{session_key}")
async def analyze_upload(state_file: UploadFile = File(...),
                         username=None,
                         session_key=None):
    """
    提交state文件
    :param session_key: 唯一ID/项目ID
    :param username: 用户名
    :return:
    """
    content = await state_file.read()
    raw_data = parser(content)
    return return_raw_data(raw_data)


@router.post("/get/{username}/{session_key}")
async def get_analyze_report(username,
                             session_key,
                             filter: FilterParams = None):
    """
    获取解析报告
    :param session_key: 唯一ID/项目ID
    :param username: 用户名
    :param filter: FilterParams
    :param params: FilterParams
    :return:
    """
    content_list = get_content(username, session_key)
    query_sets = parser(content_list,
                        filter_params=filter)
    return return_raw_data(query_sets.format())


@router.post("/query/{username}/{session_key}")
async def query_analyze_report(username,
                             session_key,
                             params: AnalyzeModel = None):
    """
    检索资源
    支持多维度、多精度的关键字匹配
    例如：
     "LB"： 返回LB信息
     "ins-": 包含ins内容
     "na": 包含na地域的资源
     "cncm.com": 匹配cncm.com精度最高的资源
    :param session_key: 唯一ID/项目ID
    :param username: 用户名
    :param params: FilterParams
    :return:
    """
    content_list = get_content(username, session_key)
    query_sets = parser(content_list,
                        filter_params=params.filter,
                        query_params=params.query)
    return return_raw_data(query_sets.format())
