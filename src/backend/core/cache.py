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
import pickle
import datetime
import copy
import logging
from functools import wraps


class CacheData(dict):
    def __init__(self, data, ttl):
        super(CacheData, self).__init__()
        self['data'] = data
        self['recorder_time'] = self.now
        self['live_time'] = self.now + int(ttl)
        self.ttl = ttl

    @property
    def now(self):
        return datetime.datetime.now().timestamp()

    def is_alive(self):
        return self.now - self['recorder_time'] < self.ttl

    def pickle_serialize(self):
        return pickle.dumps(self)

    @staticmethod
    def unpickle_serialize(data):
        return pickle.load(data)


class CacheStd(object):
    NULL_VALUE = "##%%$$##"
    CACHE_TYPE = 'Default'

    def __init__(self, ttl, enable_cache=True):
        self.ttl = ttl
        self.enable = enable_cache

    def _save(self, _id, data):
        raise NotImplementedError()

    def _read(self, _id):
        raise NotImplementedError()

    def _del(self, _id):
        raise NotImplementedError()

    def _exist(self, _id):
        raise NotImplementedError()

    def exist(self, _id):
        return self._exist(_id)

    def destroy(self):
        pass

    def renew(self):
        pass

    def delete(self, _id):
        try:
            self._del(_id)
        except KeyError:
            pass

    def save(self, _id, data):
        if self.enable:
            cache_data = CacheData(data, self.ttl)
            self._save(_id, cache_data)

    def read(self, _id):
        if self.enable is False:
            return self.NULL_VALUE
        if self.exist(_id):
            data = self._read(_id)
        else:
            return self.NULL_VALUE
        if data.is_alive is False:
            self._del(_id)
            return self.NULL_VALUE
        else:
            return data['data']

    def close_cache(self):
        self.enable = False

    def enable_cache(self):
        self.enable = True


class FileCacheStd(CacheStd):
    """
    文件缓存
    """
    CACHE_TYPE = 'File'

    def __init__(self, cache_path, ttl, enable_cache=True):
        super(FileCacheStd, self).__init__(ttl, enable_cache=enable_cache)
        self.cache_path = cache_path
        self.ttl = ttl

    def _save(self, _id, data):
        path = os.path.join(self.cache_path, _id)
        if os.path.exists(self.cache_path) is False:
            try:
                os.makedirs(self.cache_path)
            except:
                pass
        with open(path, "wb") as f:
            pickle.dump(data, f, 1)

    def _read(self, _id):
        path = os.path.join(self.cache_path, _id)
        with open(path, "rb") as f:
            data = pickle.load(f)
        return data

    def _del(self, _id):
        path = os.path.join(self.cache_path, _id)
        os.remove(path)

    def _exist(self, _id):
        path = os.path.join(self.cache_path, _id)
        return os.path.exists(path)


class MemCacheStd(CacheStd):
    """
    内存缓存
    """
    CACHE_TYPE = 'Mem'

    def __init__(self, ttl=36000, enable_cache=True):
        super(MemCacheStd, self).__init__(ttl, enable_cache=enable_cache)
        self.data_cache = {}
        self.ttl = ttl

    def _save(self, _id, data):
        self.data_cache[_id] = data

    def _exist(self, _id):
        return _id in self.data_cache

    def _read(self, _id):
        return self.data_cache[_id]

    def _del(self, _id):
        del self.data_cache[_id]

    def destroy(self):
        del self.data_cache

    def renew(self):
        self.destroy()
        self.data_cache = {}


class ComponentFileCacheStd(FileCacheStd):
    """
    Component的文件缓存
    """
    CACHE_TYPE = 'ComponentFile'

    def __init__(self, component):
        super(ComponentFileCacheStd, self).__init__(
            component.options['CACHE_PATH'],
            component.options['CACHE_TTL'])
        self.component = component


class ComponentMemCacheStd(MemCacheStd):
    """
    component的内存缓存
    """
    CACHE_TYPE = 'ComponentMem'

    def __init__(self, component):
        super(ComponentMemCacheStd, self).__init__(
            component.options['CACHE_TTL'])
        self.component = component


def make_hash(o):
    """
    Makes a hash from a dictionary, list, tuple or set to any level, that contains
    only other hashable types (including any lists, tuples, sets, and
    dictionaries).
    """
    if isinstance(o, (set, tuple, list)):

        return tuple([make_hash(e) for e in o])

    elif not isinstance(o, dict):

        return hash(o)

    try:
        new_o = copy.deepcopy(o)
    except:
        # 无法深度的即使用随机数，即不使用缓存
        new_o = {}
    for k, v in new_o.items():
        new_o[k] = make_hash(v)
    return hash(tuple(frozenset(sorted(new_o.items()))))


def get_cache_cls(cache_type) -> CacheStd:
    return {
        'MEM': MemCacheStd,
        'FILE': FileCacheStd,
    }[cache_type]


class QueryCache(object):
    _inst = None

    def __new__(cls, *args, **kwargs):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst

    def __init__(self):
        self.cache_engine = get_cache_cls("MEM")()

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            run_cache_key = make_hash(("get_content", args, kwargs))
            if self.cache_engine.exist(run_cache_key):
                logging.info(f"Hit Cache! { args, kwargs}")
                return self.cache_engine.read(run_cache_key)
            else:
                res = func(*args, **kwargs)
                self.cache_engine.save(run_cache_key, res)
                return res
        return wrapper

    def renew(self):
        return self.cache_engine.renew()

    def renew_func(self, func, *args, **kwargs):
        run_cache_key = make_hash(("get_content", args, kwargs))
        return self.cache_engine.delete(run_cache_key)


global_cache = QueryCache()
