# coding: utf-8
import json
import random
import re
import sys

import SparkApi

sys.path.append("spark/SparkApi.py")

# 以下密钥信息从控制台获取   https://console.xfyun.cn/services/bm35
appid = "b57c4603"  # 填写控制台中获取的 APPID 信息
api_secret = "YzAzNDMwYzJiMDFmZjBjOWY0NDI4YjUw"  # 填写控制台中获取的 APISecret 信息
api_key = "bb79bcff10b39c11902b85fee6cf5d8c"  # 填写控制台中获取的 APIKey 信息

domain = "generalv3.5"      # Max版本
# domain = "4.0Ultra"  # Ultra版本

Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"   # Max服务地址
# Spark_url = "wss://spark-api.xf-yun.com/v4.0/chat"  # Ultra服务地址


def getText(text, role, content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text


def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length


def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text


def get_output(charges, all_keys):
    # 初始上下文内容，当前可传system、user、assistant 等角色
    # charges = "'诈骗', '敲诈勒索'"
    text = [
        {"role": "system", "content": f"你是一位法律领域的专家，精通中文文本的关键词提取任务。你的任务是根据用户提供的案例关键词，结合该关键词的具体意义，将其中具有和{charges}等有关的关键词提取出来。\
        请严格遵循以下步骤进行操作：\
        1. 仔细阅读并理解用户提供的词汇列表。\
        2. 确定每个词汇的具体含义，判断是否与{charges}相关。若相关，则保留为有效关键词。\
        3. 根据该词语的词性、法律意义、适用场景等提取出初步的有效关键词列表。\
        4. 检查提取出的关键词中是否有遗漏、无关或不准确的关键词，必要时进行删除或修正。\
        5. 确保最终列表长度大于25。\
        6. 输出只包括按照json格式的关键词列表结果。\
        用户输入为多个案件提取的词语列表，输出为json格式的列表。\
        input: ['关键词1'，'关键词2', ...]。\
        output: ['关键词1', '关键词2', '关键词3', ...]"
        },
    ]

    llm_list = []
    print("星火回答中...")
    for i in range(3):
        print(f"\n================= {i+1}-round ====================")
        input_data = str(random.sample(all_keys, 200))
        #
        # print("=================== input_data =================")
        # print(input_data)
        question = checklen(getText(text, "user", input_data))
        SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
        # 去除重复项并转换为列表
        # print("\n=================== SparkApi.answer =================")
        keywords = list(set(extract_keywords(SparkApi.answer)))
        llm_list.extend(keywords)
        print("\n==========keywords==========")
        print(keywords)

    return llm_list


# 提取回答中的关键次部分
def extract_keywords(text):
    # 正则表达式匹配 JSON 格式的数组或对象中包含的列表内容
    # 匹配对象格式：{"关键词": [ ... ]}
    json_object_pattern = r'"关键词"\s*:\s*(\[[^\]]*\])'

    # 匹配直接的 JSON 数组格式
    json_array_pattern = r'\[\s*(?:".*?"(?:\s*,\s*)?)*\s*\]'

    # 使用正则表达式搜索匹配 JSON 对象中的关键词列表
    match_object = re.search(json_object_pattern, text, re.DOTALL)
    if match_object:
        json_string = match_object.group(1)
        try:
            json_list = json.loads(json_string)
            return json_list
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return []

    # 如果未找到对象格式，则尝试查找 JSON 数组格式
    match_array = re.search(json_array_pattern, text, re.DOTALL)
    if match_array:
        json_string = match_array.group(0)
        try:
            json_list = json.loads(json_string)
            return json_list
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            return []

    print("没有找到有效的 JSON 列表")
    return []


# if __name__ == '__main__':
#     Input = "['签订', '提交', '虚假', '审核', '承认', '经营', '户籍', '付款', '不予', '利息', '打电话', '负责人', '拒绝', '受伤', '阻止', '医院', '做', '期限', '组', '协调', '收缴', '法律', '证明书', '同伙', '常住', '更换', '组长', '打开', '上午', '新', '实施', '偿款', '线索', '询问', '公路', '犯数', '本院', '取款', '检察', '重伤', '侦破', '取现', '法规', '承诺', '感谢', '支行', '有限', '合同书', '业务', '双', '农业', '导致', '建设', '房地产', '贸易', '请求', '不等', '管理', '生活', '合计', '照片', '关系', '悔罪', '职务', '损坏', '轻微', '强行', '中国', '本市', '支', '许可证', '次', '台', '右手', '余款', '村', '吨', '龙岩市', '人民币', '住宿', '装有', '斗殴', '退缴', '厦门市', '借款', '戴', '支持', '存款', '留下', '物证', '刑罚', '警察', '辨认', '安装', '下属', '真实', '主动', '路边', '分述', '组织', '社区', '代表人', '还款']"
#     # Input = []
#     # with open("../temp.txt", 'r', encoding='utf-8') as f:
#     #     for line in f:
#     #         Input.append(line)
#     # question = checklen(getText("user", Input))
#     SparkApi.answer = ""
#     print("星火:", end="")
#     # SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
#     # getText("assistant", SparkApi.answer)
#     get_output("'诈骗', '敲诈勒索'", Input)
