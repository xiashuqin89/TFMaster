"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from fastapi import Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse


def return_raw_data(raw_data):
    results = []
    for vendor, info in raw_data.items():
        data = {
            "vendor": vendor,
            "resources": []
        }
        for k, v in info.items():
            data["resources"].append(
                {"instances": [i.to_json() for i in v], "count": len(v)}
            )
        results.append(data)
    return results


async def swagger_ui_html(req: Request, openapi_url) -> HTMLResponse:
    root_path = req.scope.get("root_path", "").rstrip("/")
    openapi_url = root_path + openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="V1" + " - Swagger UI",
        oauth2_redirect_url=None,
        init_oauth=None,
        swagger_ui_parameters=None,
    )
