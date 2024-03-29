"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from functools import partial

from middleware.http import RestfullMiddleware
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from core.utils import swagger_ui_html
from apis.analyze import router as analyze_router
from apis.state import router as state_mng_router
from apis.cli import router as cli_router
from setting.config import options


base_app = FastAPI()
v1_app = FastAPI()

v1_app.include_router(analyze_router, prefix="/analyze")
v1_app.include_router(state_mng_router, prefix="/state")
v1_app.include_router(cli_router, prefix="/cli")
base_app.add_route("/docs/v1", partial(swagger_ui_html,
                                       openapi_url="/tfmasterparser/openapi/v1.json"),
                   include_in_schema=False)
base_app.mount("/v1", v1_app)
v1_app.middleware("http")(RestfullMiddleware(v1_app))
v1_app.add_middleware(
    CORSMiddleware,
    allow_origins=options["ALLOW_ORIGINS"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@v1_app.get("/")
async def test():
    return "Hello World, This is V1 APIS"


# 重新定义OpenAPI的URL
@base_app.get("/tfmasterparser/openapi/v1.json")
@base_app.get("/openapi/v1.json")
async def v1_openapi():
    return get_openapi(
        title="Custom OpenAPI",
        version="1.0.0",
        routes=v1_app.routes,
    )


if __name__ == '__main__':
    import sys
    import uvicorn
    for router in v1_app.routes:
        print(router)
    try:
        uvicorn.run(base_app, host="0.0.0.0", port=int(sys.argv[1]))
    except Exception as e:
        uvicorn.run(base_app, host="0.0.0.0", port=18083)
