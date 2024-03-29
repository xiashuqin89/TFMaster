"""
Tencent is pleased to support the open source community by making 蓝鲸智云 - 监控平台 (BlueKing - Monitor) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import datetime
import hashlib
import base64

from Crypto.Cipher import AES
from fastapi import APIRouter
from fastapi import File, UploadFile
from core.storage import StateMng
from core.exception import CLITokenRequestException, CLITokenExpiredException
from apis.analyze import get_content
from core.cache import global_cache
from setting.config import options

router = APIRouter()

SALT_KEY = options["SALT_KEY"]
BLOCK_SIZE = 16  # Bytes


def pad(s):
    """
    :param s:
    :return:
    """
    return s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(
        BLOCK_SIZE - len(s) % BLOCK_SIZE)


def unpad(s):
    """
    :param s:
    :return:
    """
    return s[: -ord(s[len(s) - 1:])]


class SessionMng(object):
    @classmethod
    def get_salt_key(cls):
        key = f"{SALT_KEY}".encode("utf-8")
        return hashlib.md5(key).hexdigest()

    @classmethod
    def get_token(cls, username, session_key):
        salt_key = cls.get_salt_key()
        date = str(int(datetime.datetime.now().timestamp()))
        return cls.encode(salt_key, f"{username}&{session_key}&{date}")

    @classmethod
    def get_info_from_token(cls, token):
        return cls.decode(cls.get_salt_key(), token).split("&")

    @classmethod
    def decode(cls, salt_key, content):
        return cls.aes_decrypt(salt_key, content)

    @classmethod
    def encode(cls, salt_key, content):
        return cls.aes_encrypt(salt_key, content)

    @classmethod
    def aes_encrypt(cls, key, data):
        """
        :param key:
        :param data:
        :return:
        """
        key = key.encode("utf8")
        # 字符串补位
        data = pad(data)
        cipher = AES.new(key, AES.MODE_ECB)
        # 加密后得到的是bytes类型的数据，使用Base64进行编码,返回byte字符串
        result = cipher.encrypt(data.encode())
        encodestrs = base64.b64encode(result)
        enctext = encodestrs.decode("utf8")
        return enctext

    @classmethod
    def aes_decrypt(cls, key, data):
        """
        :param key: 密钥
        :param data: 加密后的数据（密文）
        :return:明文
        """
        key = key.encode("utf8")
        data = base64.b64decode(data)
        cipher = AES.new(key, AES.MODE_ECB)
        # 去补位
        text_decrypted = unpad(cipher.decrypt(data))
        text_decrypted = text_decrypted.decode("utf8")
        return text_decrypted


@router.post("/get_token/{username}/{session_key}")
async def cli_get_token(
        username,
        session_key
):
    """
    获得用户TOken
    :param username:
    :param session_key:
    :return:f
    """
    return SessionMng.get_token(username, session_key)


@router.post("/upload/{token}")
async def cli_upload(
        token,
        state_file: UploadFile = File(...)
):
    """
    提交state文件
    :param token:
    :param state_file:
    :return:f
    """
    try:
        username, session_key, date = SessionMng.get_info_from_token(token)
        token_time = datetime.datetime.fromtimestamp(int(date))
        if datetime.datetime.now() - datetime.timedelta(days=1) > token_time:
            raise CLITokenExpiredException(token_time)
    except CLITokenExpiredException as e:
        raise e
    except:
        raise CLITokenRequestException(token)
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
