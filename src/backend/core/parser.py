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
import json
import typing
import yaml
import copy
import heapq
from collections import defaultdict
from difflib import SequenceMatcher as SM
from pydantic import BaseModel, Field as PYField
from prettydiff import diff_json, get_annotated_lines_from_diff, Flag, \
    print_diff


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


class ChangeInfo(object):
    NO_OPS, ADD, UPDATE, DELETE = 0, 1, 2, 3

    def __init__(self, data):
        self.data = data

    @property
    def address(self):
        return self.data["address"]

    @property
    def change(self):
        return self.data["change"]

    @property
    def actions(self):
        return self.change["actions"]

    @property
    def need_update(self):
        return "update" in self.actions

    @property
    def need_delete(self):
        return "delete" in self.actions

    @property
    def need_add(self):
        return "create" in self.actions

    @property
    def before(self):
        return self.change["before"]

    @property
    def after(self):
        return self.change["after"]

    def get_state(self):
        if self.need_add:
            return self.ADD
        if self.need_update:
            return self.UPDATE
        if self.need_delete:
            return self.DELETE
        return self.NO_OPS

    def get_diff(self):
        diff_info = diff_json(
            self.before, self.after
        )
        return diff_info

    def diff_content(self):
        diff_info = self.get_diff()
        lines = get_annotated_lines_from_diff(diff_info)
        results = ''
        for line in lines:
            if Flag.ADDED in line.flags:
                flags = f"+ "
            elif Flag.REMOVED in line.flags:
                flags = f"- "
            else:
                flags = "  "
            results += flags + "\n"
            results += " " * (2 * line.indent) + "\n"
            results += line.s + "\n"
        return results

    def to_json(self):
        return {
            "state": self.get_state(),
            "before": self.before,
            "after": self.after,
            "diff": self.get_diff(),
            "diff_show": self.diff_content()
        }


class Resource(object):
    def __init__(self, data):
        self.data = data
        self.changes: typing.Union[typing.List[ChangeInfo], typing.Any] = None

    @property
    def address(self):
        return self.data["address"]

    def super_get(self, key, default=None):
        """
        TODO 需要支持 list 和 dict获取
        :param key:
        :param default:
        :return:
        """
        try:
            return self.data[key]
        except KeyError:
            return default

    def get_property(self, target, axis=None):
        def _get_attr(obj, k):
            if obj is None:
                return None
            if isinstance(obj, dict):
                return obj.get(k)
            elif isinstance(obj, list):
                try:
                    return obj[int(k)]
                except:
                    pass
                result = []
                for o in obj:
                    r = _get_attr(o, k)
                    result.append(r)
                return result
            elif obj:
                return obj.super_get(k) if hasattr(obj,
                                                   'super_get') else getattr(
                    obj, k)

        def _get(obj, key):
            if "." in key:
                return _get(
                    _get_attr(obj, key.split(".")[0]),
                    key.split(".", maxsplit=1)[1]
                )
            elif isinstance(key, list):
                res = []
                for k in key:
                    res.append(
                        _get(obj, k)
                    )
                # TODO 当如果返回值的个数不一致时需要补齐
                return res if axis is None else list(zip(*res))
            else:
                return _get_attr(obj, key)

        return _get(self, target)


class Field(object):
    def __init__(self, key, desc=None):
        self.key = key
        self.desc = desc or ""
        self.value = None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"k={self.key},v={self.value}"

    def to_json(self):
        return {
            "key": self.key,
            "value": self.value,
            "desc": self.desc
        }


class Block(object):
    def __init__(self, block_id, name, fields: typing.List[Field], group,
                 vendor):
        self.block_id = block_id
        self.fields = fields + [Field("resource_address")]
        self.name = name
        self.group = group
        self.vendor = vendor
        self.resource = None

    def set_resource(self, resource):
        self.resource = resource

    def set_field_value(self, key, value):
        for f in self.fields:
            if f.key == key:
                f.value = value

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Block({self.name},fields={self.fields})"

    def to_json(self):

        return {
            "group": self.group,
            "name": self.name,
            "fields": [f.to_json() for f in self.fields],
            "change": self.change_info
        }

    @property
    def change_info(self):
        return self.resource.changes.to_json() if self.resource.changes else {}

    @property
    def change_state(self):
        state = self.change_info["state"]
        if state in [ChangeInfo.NO_OPS]:
            return "N#$%@#$%O-N#$%@#$%23O#$%@#$%"
        elif state in [ChangeInfo.DELETE]:
            return "change delete"
        elif state in [ChangeInfo.ADD]:
            return "change add"
        elif state in [ChangeInfo.UPDATE]:
            return "change update"
        return ""


class Policy(object):
    def __init__(self, policy):
        self.policy = policy

    @property
    def fields(self):
        return self.policy["fields"]

    @property
    def policy_type(self):
        return self.policy["type"]

    @property
    def name(self):
        return self.policy["name"]

    @property
    def group(self):
        return self.policy["group"]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"MappingPolicy({self.name})"


class MappingPolicy(Policy):
    @property
    def mapping_spec(self):
        return self.policy["specs"]

    @property
    def bind_block(self):
        return self.policy["block"]

    @property
    def bind_resource(self):
        return self.policy["resource"]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"MappingPolicy({self.bind_resource}:{self.bind_block})"


class PolicyManager(object):
    def __init__(self, policy_list):
        self.policy_list = [Policy(policy_stream) if policy_stream["type"] in [
            "Block"] else MappingPolicy(policy_stream) for policy_stream in
                            policy_list]

    def get_mapping_policy(self):
        results = dict()
        for policy in self.policy_list:
            if policy.policy_type in ["ResourceMapping"]:
                for vendor, spec in policy.mapping_spec.items():
                    results[spec["resource"]] = policy
        return results

    def get_block_policy(self):
        return {policy.name: policy for policy in self.policy_list if
                policy.policy_type in ["Block"]}


class QueryBlockHeapNode(object):
    LONGEST_COMMON, CHAR_SIMILAR = 0, 1

    def __init__(self,
                 block,
                 query_str,
                 keys=None,
                 sim_type=LONGEST_COMMON):
        self.block = block
        self.query_str = query_str
        self.keys = keys or ["name", "vendor", "group", "change_state"]
        self.ratio = 0
        self.sim_type = sim_type
        self.ratio_config = {
            "name": (100, self.LONGEST_COMMON),
            "vendor": (100, self.LONGEST_COMMON),
            "group": (100, self.LONGEST_COMMON),
            "change_state": (100, self.LONGEST_COMMON),
            "fields_value": (100, self.LONGEST_COMMON)
        }
        self.calc_score_record = defaultdict(float)
        self.calc_score()

    @classmethod
    def longest_common_substring(cls, str1, str2):
        m = len(str1)
        n = len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        max_length = 0
        end_index = 0
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1].lower() == str2[j - 1].lower():
                    dp[i][j] = dp[i - 1][j - 1] + 1
                    if dp[i][j] > max_length:
                        max_length = dp[i][j]
                        end_index = i
        start_index = end_index - max_length
        longest_substring = str1[start_index:end_index]
        return longest_substring

    @classmethod
    def _calc_str_sim_ratio(cls, a, b, sim_type):
        """
        计算相似度
        """
        # a为短，b为长
        a, b = (b, a) if len(a) > len(b) else (a, b)
        t = 0
        c = 0
        batch_num = 0
        for _b in b.split(" "):
            if a == "None" or _b == "None":
                 continue
            if sim_type == cls.CHAR_SIMILAR:
                batch_num = SM(None, a, _b).ratio()
            elif sim_type == cls.LONGEST_COMMON:
                sub = cls.longest_common_substring(a, _b)
                s, l = (_b, a) if len(a) > len(_b) else (a, _b)
                if len(sub) <= 1:
                    continue
                batch_num = float(len(sub) / len(l))
            t += batch_num
            if batch_num > 0:
                c += 1
            batch_num = 0
        return t / (c if c else 1)
        # if self.sim_type == self.CHAR_SIMILAR:
        #     return SM(None, a, b).ratio()
        # else:
        #     sub = self.longest_common_substring(a, b)
        #     s, l = (b, a) if len(a) > len(b) else (a, b)
        #     return float(len(sub) / len(l))

    def calc_property_score(self, key):
        self.calc_score_record[key] = self._calc_str_sim_ratio(
            getattr(self.block, key), self.query_str, self.ratio_config[key][1])

    def calc_fields_score(self):
        count = 1
        for field in self.block.fields:
            count += 1
            self.calc_score_record["fields_value"] += self._calc_str_sim_ratio(
                str(field.value),
                self.query_str, self.CHAR_SIMILAR)
        self.calc_score_record["fields_value"] = \
            self.calc_score_record["fields_value"] / count

    def calc_score(self):
        for key in self.keys:
            self.calc_property_score(key)
        self.calc_fields_score()

        for key, value in self.ratio_config.items():
            self.ratio += self.calc_score_record[key] * value[0]

    def __lt__(self, other):
        return self.ratio < other.ratio


class FilterParams(BaseModel):
    vendor: str = PYField(default=None)
    block_name: str = PYField(default=None)
    change_state: str = PYField(default=None)
    group: str = PYField(default=None)


class QueryParams(BaseModel):
    query_str: str = PYField(default=None)
    count: int = PYField(default=10, description="返回结果集")
    keys: list = PYField(default=[])
    similar_type: int = PYField(default=0, description="相似度算法，0:最长子串，1:字符串近似")


class ResultSets(object):
    def __init__(self):
        self.sets = defaultdict(lambda: defaultdict(list))
        self.block_list = list()

    @classmethod
    def new_self(cls, block_list):
        r = ResultSets()
        r.block_list = block_list
        return r

    def add_block(self, vendor, block_name, block):
        if block.block_id not in [_block.block_id for _block in
                                  self.block_list]:
            self.block_list.append(block)
            self.sets[vendor][block_name].append(block)

    def query(self, query_params: QueryParams):
        query_result = []
        for block in self.block_list:
            heapq.heappush(query_result,
                           QueryBlockHeapNode(block,
                                              query_params.query_str,
                                              query_params.keys,
                                              query_params.similar_type))
        for i in heapq.nlargest(query_params.count,
                                query_result):
            print(i.ratio, i.query_str, i.block, i.calc_score_record)
        return self.new_self(
            [i.block for i in heapq.nlargest(query_params.count,
                                             query_result)])

    def extend(self, result_set):
        self.block_list.extend(result_set.block_list)

    def filter(self, filter_params: FilterParams):
        """
        过滤
        """
        result = []
        for block in self.block_list:
            # 过滤非云
            if filter_params.vendor \
                    and block.vendor != filter_params.vendor:
                continue
            # 过滤非block
            if filter_params.block_name \
                    and block.name != filter_params.block_name:
                continue
            # 过滤无变化的
            if filter_params.change_state and filter_params.change_state in "change" and \
                "change" not in filter_params.change_state:
                continue

            # 过滤变化符合预期
            if filter_params.change_state \
                    and block.change_state != filter_params.change_state:
                continue
            # 过滤非group
            if filter_params.group \
                    and block.group != filter_params.group:
                continue
            result.append(block)
        return self.new_self(result)

    def format(self):
        results = defaultdict(lambda : defaultdict(list))
        for block in self.block_list:
            results[block.vendor][block.name].append(block)
        return results


class ParserEngine(object):
    def __init__(self, data,
                 policy_manager: PolicyManager):
        self.data = data
        self.policy_manager = policy_manager
        self.block_cache = dict()

    def get_modules_resources(self, modules, temp):
        """
        :param modules:
        :return:
        """
        if "resources" in modules:
            temp.extend(modules["resources"])
        if "child_modules" in modules:
            for child_module in modules["child_modules"]:
                self.get_modules_resources(child_module, temp)

    def parser_change(self):
        """
        解析变化的部分
        :return:
        """
        change_resources = self.data["resource_changes"]
        return [
            ChangeInfo(change_resource) for change_resource in change_resources
        ]

    def try_get_region(self):
        """
        从配置中获取
        :return:
        """
        try:
            return \
            self.data["configuration"]["root_module"]["variables"]["region"][
                "default"]
        except KeyError:
            return 'None'

    def parser(self):
        def f():
            return defaultdict(list)

        result_set = ResultSets()
        region = self.try_get_region()
        resources_list = []
        self.get_modules_resources(
            self.data["prior_state"]["values"]["root_module"],
            resources_list)
        self.get_modules_resources(
            self.data["planned_values"]["root_module"],
            resources_list)
        change_mapping = {change.address: change for change in
                          self.parser_change()}
        mapping_policy = self.policy_manager.get_mapping_policy()
        block_policy = self.policy_manager.get_block_policy()
        for resource_dict in resources_list:
            if resource_dict["type"] in mapping_policy \
                    and mapping_policy[resource_dict["type"]].bind_block \
                    in block_policy:
                mp_rule = mapping_policy[resource_dict["type"]]
                resource = Resource(resource_dict)
                if resource.address in change_mapping:
                    resource.changes = change_mapping[resource.address]
                block_rule = block_policy[
                    mapping_policy[resource_dict["type"]].bind_block]
                block = self.new_block(resource.address, block_rule)
                for vendor, info in mp_rule.mapping_spec.items():
                    for key, value in info["specs"].items():
                        block.set_field_value(key,
                                              resource.get_property(value))
                    block.set_field_value("region", region)
                    block.set_field_value("resource_address", resource.address)
                    block.resource = resource
                    block.vendor = vendor
                    result_set.add_block(vendor, block.name, block)
        return result_set

    def new_block(self, block_id, policy: Policy):
        if block_id not in self.block_cache:
            print(block_id, self.block_cache)
            self.block_cache[block_id] = Block(
                block_id,
                policy.name,
                [Field(field["key"], field.get("desc")) for field in
                 policy.fields],
                policy.group,
                None
            )
        return self.block_cache[block_id]


def parser(content_list,
           filter_params=None,
           query_params=None):
    policy_list = []
    for root, dirs, files in os.walk("models"):
        for file in files:
            policy_list.extend(
                yaml.safe_load_all(open(os.path.join(
                    root, file
                )).read())
            )
    query_sets = None
    for content in content_list:
        pe = ParserEngine(
            json.loads(content),
            PolicyManager(policy_list)
        )
        if query_sets is None:
            query_sets = pe.parser()
        else:
            query_sets.extend(pe.parser())
    if filter_params:
        query_sets = query_sets.filter(filter_params)
    if query_params:
        query_sets = query_sets.query(query_params)
    return query_sets
