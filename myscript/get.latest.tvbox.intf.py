import os
import requests
import base64
import re
import json
from pypinyin import lazy_pinyin, Style


def is_valid_json(json_str):
    try:
        # 先检查是否为字符串类型
        if not isinstance(json_str, str):
            return False
            # 尝试解析
        json.loads(json_str)
        return True
    except (ValueError, json.JSONDecodeError):
        return False


def parse_config_file(file_path):
    # 初始化一个空列表，用于存储解析后的数据 
    parsed_data = []
    try:
        # 以只读模式打开指定的配置文件 
        with open(file_path, 'r', encoding="utf-8") as file:
            # 逐行读取文件内容 
            for line in file:
                # 去除行首尾的空白字符 
                line = line.strip()
                # 检查该行是否为空或是否以 '#' 开头 
                if not line or line.startswith('#'):
                    # 如果是注释行或空行，则跳过 
                    continue
                    # 使用逗号分割当前行的内容
                elements = line.split(',')
                # 检查分割后的元素数量是否为 3 
                if len(elements) == 3:
                    # 去除每个元素首尾的空白字符 
                    name, value1, value2 = [elem.strip() for elem in elements]
                    # 将解析后的元素作为一个元组添加到 parsed_data 列表中 
                    parsed_data.append((name, value1, value2))
                else:
                    # 如果元素数量不为 3，打印错误信息 
                    print(f"Invalid line: {line}. Expected 3 elements, got {len(elements)}.")
    except FileNotFoundError:
        # 如果文件未找到，打印错误信息 
        print(f"File {file_path} not found.")
    return parsed_data


def get_json_content(intf_url=""):
    try:
        headers = {'User-Agent': 'okhttp'}
        response = requests.get(intf_url, headers=headers)
        if response.status_code == 200:
            content = response.text
            if is_valid_json(content):
                return response.content.decode('utf-8')
            elif "**" in content:
                return base64_decode(content)
            return content
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return None


def base64_decode(input_str):
    b64_str = extract_id(input_str)
    # print(b64_str)
    decoded_bytes = base64.b64decode(b64_str)
    decoded_str = decoded_bytes.decode('utf-8')
    return decoded_str


def extract_id(input_str):
    # 编译正则表达式（匹配至少8位字母数字）
    pattern = re.compile(r'[0-9A-Za-z]{8}\*\*')
    # 查找pattern
    parts = pattern.split(input_str)
    # print(parts)
    return parts[1]


def json_str_format(raw_str):
    lines = [line for line in raw_str.splitlines() if line.strip() and not line.strip().startswith("//")]

    new_str = '\n'.join(lines)
    return new_str


def safe_json_write(raw_str, file_path):
    """
    将字符串安全转换为JSON格式并写入文件
    :param raw_str: 待处理字符串（需符合JSON格式）
    :param file_path: 输出文件路径
    """
    raw_str1 = json_str_format(raw_str)
    try:
        # 步骤1：尝试解析字符串为JSON对象
        json_obj = json.loads(raw_str1)  # [3]()[4]()

        # 步骤2：格式化写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_obj, f,
                      indent=4,  # 缩进4字符增强可读性 [7]()[9]()
                      ensure_ascii=False)  # 支持非ASCII字符（如中文）
        print(f"JSON已成功写入：{file_path}")

    except JSONDecodeError as e:
        print(f"JSON解析失败：{str(e)} → 请检查字符串格式")  # [3]()[4]()
    except IOError as e:
        print(f"文件操作错误：{str(e)} → 请检查路径权限")
    except Exception as e:
        print(f"未知错误：{str(e)}")


# 示例使用
if __name__ == "__main__":
    cur_dir = os.getcwd()
    config_file_path = os.path.join(cur_dir, "config\\tvbox.intf.cfg")
    print(config_file_path)
    # 替换为你的配置文件路径 
    # file_path = 'config.txt'  
    # 调用解析函数 
    result = parse_config_file(config_file_path)
    # 打印解析结果 
    for item in result:
        # print(item)
        name = ''.join(lazy_pinyin(item[0], style=Style.NORMAL))
        file_name = name + ".json"
        # print(name)
        url = item[1]
        print(url)
        content = get_json_content(url)
        # print(content)
        # safe_json_write(content, file_name)
        if content:
            safe_json_write(content, file_name)
        # with open(os.path.join(os.getcwd(), '1'+file_name), "w",encoding='utf-8') as f:
        #     f.write(json_str_format(content))
