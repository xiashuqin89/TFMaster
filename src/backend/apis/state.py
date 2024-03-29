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
from typing import Dict, Union

from core.storage import StateMng
from fastapi import File, UploadFile
from fastapi import APIRouter
from apis.analyze import get_content
from core.cache import global_cache
from pydantic import BaseModel

router = APIRouter()


class StateFile(BaseModel):
    state_file: Union[Dict, None]


@router.post("/upload/{username}/{session_key}")
async def upload_tf_state(
        username,
        session_key,
        state_file: UploadFile = File(...)
):
    """
    提交state文件
    :param state_file:
    :param session_key: 唯一ID/项目ID
    :param username: 用户名
    :return:f
    """
    content = await state_file.read()
    filename = "latest.json"
    with StateMng(username, session_key) as sm:
        sm.push(state_file.filename or filename,
                content,
                force_replace=True)
    global_cache.renew_func(
        get_content,
        username,
        session_key
    )
    return "success"


@router.post("/upload_json/{username}/{session_key}")
def upload_tf_state_json(
        username,
        session_key,
        state_file: StateFile
):
    """
    提交state文件
    :param state_file:
    :param session_key: 唯一ID/项目ID
    :param username: 用户名
    :return:f
    """
    with StateMng(username, session_key) as sm:
        sm.push("latest.json",
                json.dumps(state_file.dict()),
                force_replace=True)
    global_cache.renew_func(
        get_content,
        username,
        session_key
    )
    return "success"
