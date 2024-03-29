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
import copy
import logging
import traceback

from core.exception import REST_EXCEPTIONS
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from fastapi import FastAPI, Request


class RestfullMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app

    async def __call__(self, request: Request, call_next):
        base_format = {"code": 0,
                       "data": [],
                       "message": "Success"
                       }
        return_result = copy.deepcopy(base_format)
        try:
            response = await call_next(request)
            if isinstance(response, StreamingResponse):
                content = b""
                async for chunk in response.body_iterator:
                    content += chunk
                if response.status_code == 200:
                    return_result["data"] = json.loads(content.decode("utf-8"))
                else:
                    return_result["data"] = content.decode("utf-8")
                    return_result["code"] = response.status_code
            else:
                return_result["data"] = response
        except REST_EXCEPTIONS as e:
            return_result["message"] = e.msg
            return_result["code"] = e.status_code
        except Exception as e:
            return_result["message"] = str(e)
            return_result["code"] = '9999'
            logging.error(traceback.format_exc())
        return JSONResponse(return_result)
