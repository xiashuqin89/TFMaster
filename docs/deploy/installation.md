# TFMaster 部署文档

## 依赖第三方组件

* Python >= 3.8.0
* Nodejs   >= 14.21.3
* Terraform >= v1.6.3
* BK-REPO

## TFMaster 后端部署

后段代码目录
```shell
├── Dockerfile
├── README.md
├── __init__.py
├── apis
├── core
├── main.py
├── middleware
├── models
├── requirements.txt
├── setting
└── venv
```

### 后台进程部署

```shell
# 安装依赖
pip install -r requirements.txt

# 修改配置
cd setting && cat prod.py

STORAGE_URL = os.getenv("STORAGE_URL", "") # bk-repo 服务域名
STORAGE_CODE = os.getenv("STORAGE_CODE", "") # bk-repo 生成的token密钥
STORAGE_OPERATOR = os.getenv("STORAGE_OPERATOR", "") # bk-repo 生成的token名字
SALT_KEY = os.getenv("SALT_KEY", "") # 用户自定义key
ALLOW_ORIGINS = os.getenv('ALLOW_ORIGINS', '*').split(',') # 跨域设置

# 启动
python main.py

# docker 启动
docker build -f Dockerfile --network=host -t tfmaster_backend:lastest .
docker start tfmaster_backend
```

## TFMaster 后端部署

后段代码目录
```shell
├── Dockerfile
├── Procfile
├── bk.config.js
├── index.html
├── mock-server
├── node_modules
├── paas-server
├── package-lock.json
├── package.json
├── postcss.config.js
├── replace-static-url-plugin.js
├── src
└── static
```

### 前端进程部署

```shell
# 安装依赖
npm install

# 修改配置
.bk.stag.env # for线上测试环境
.bk.production.env # for线上正式环境
.bk.deveplopment.env # for本地开发 用户需要自行创建

BK_AJAX_URL_PREFIX = '/' # 后台进程域名或者ip eg：/www.tfmaster.com
BK_USER_INFO_URL = '/user' # 获取用户登录的接口path，蓝鲸部署环境下可以不用改

# 开发
npm run dev

# 启动
npm run server

# docker 启动
docker build -f Dockerfile --network=host -t tfmaster_front:lastest .
docker start tfmaster_front
```
