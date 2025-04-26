import os
import sys
import requests
import base64
import re
import json
import csv
from pypinyin import lazy_pinyin, Style
from urllib.parse import urlparse, urlunparse


def get_base_dir_url(url):
    # 解析URL
    parsed_url = urlparse(url)

    # 获取路径部分并去掉最后一个斜杠后的部分
    path_parts = parsed_url.path.rsplit('/', 1)

    # 构建新的路径
    base_path = path_parts[0] + '/' if len(path_parts) > 1 else '/'

    # 重新构建URL
    base_url = urlunparse((
        parsed_url.scheme,  # 协议
        parsed_url.netloc,  # 主机
        base_path,  # 路径
        parsed_url.params,  # 参数
        parsed_url.query,  # 查询字符串
        parsed_url.fragment  # 片段标识符
    ))

    return base_url


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
                return intf_json_fix(intf_url, response.content.decode('utf-8'))
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


def intf_json_fix(intf_url, data):
    base_url = get_base_dir_url(intf_url)
    if './' in data:
        data = data.replace('./', base_url)
    if '../' in data:
        data = data.replace('../', base_url + '../')
    return data


def get_default_jar_url(json_name):
    with open(json_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
        # 打印读取的内容
        # print("读取的JSON内容:")
        # print(json.dumps(data, indent=4))

        # 返回解析后的数据
    default_spider = data['spider']

    return default_spider


def split_full_jar_url_string(input_str, delimiter=";md5;"):
    # 使用split方法分割字符串
    parts = input_str.split(delimiter, 1)

    # 检查分割结果
    if len(parts) == 2:
        str1, str2 = parts
        return str1, str2
    else:
        raise ValueError(f"输入字符串中没有找到分隔符 '{delimiter}'")


def get_jar_from_url(full_jar_url, jar_name):
    jar_url, jar_md5 = split_full_jar_url_string(full_jar_url)

    try:
        headers = {'User-Agent': 'okhttp'}
        response = requests.get(jar_url, headers=headers)
        with open(jar_name, "wb") as f:
            f.write(response.content)
        print('jar 成功下载到：', jar_name)
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
        return None


def parse_json_to_sites_csv(intf_name, json_file, csv_file):
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        sites_dict = data['sites']
        default_jar = data['spider']

        print(sites_dict)

        new_sites_dict_list = []

        for site in sites_dict:
            new_site = {}
            new_site['intf_name'] = intf_name
            if 'name' in site:
                new_site['name'] = site['name']
            else:
                print(f"{intf_name} site has no 'name' key, invalid!")
                sys.exit(1)

            if 'key' in site:
                new_site['key'] = site['key']
            else:
                print(f"{intf_name} site has no 'key' key, invalid")
                sys.exit(1)

            if 'name' in site:
                new_site['name'] = site['name']
            else:
                print(f"{intf_name} site has no 'name' key, invalid!")
                sys.exit(1)

            if 'type' in site:
                new_site['type'] = site['type']
            else:
                new_site['type'] = '0'

            if 'api' in site:
                new_site['api'] = site['api']
            else:
                new_site['api'] = '-'

            if 'indexs' in site:
                new_site['indexs'] = site['indexs']
            else:
                new_site['indexs'] = '0'

            if 'searchable' in site:
                new_site['searchable'] = site['searchable']
            else:
                new_site['searchable'] = '1'

            if 'quickSearch' in site:
                new_site['quickSearch'] = site['quickSearch']
            else:
                new_site['quickSearch'] = '1'

            if 'changeable' in site:
                new_site['changeable'] = site['changeable']
            else:
                new_site['changeable'] = '1'

            if 'timeout' in site:
                new_site['timeout'] = site['timeout']
            else:
                new_site['timeout'] = '15'

            if 'ext' in site:
                new_site['ext'] = site['ext']
            else:
                new_site['ext'] = '-'

            if 'jar' in site:
                new_site['jar'] = site['jar']
            else:
                new_site['jar'] = '-'

            if 'playerType' in site:
                new_site['playerType'] = site['playerType']
            else:
                new_site['playerType'] = '-1'

            if 'categories' in site:
                new_site['categories'] = site['categories']
            else:
                new_site['categories'] = '-'
            new_sites_dict_list.append(new_site)

        # # 检查数据是否为列表
        # if not isinstance(data, dict):
        #     raise ValueError("JSON数据不是字典")
        #
        # print(new_sites_dict_list[0])
        # # 获取CSV文件的字段名
        fieldnames = new_sites_dict_list[0].keys()
        # print(fieldnames)

        # 写入CSV文件
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 写入表头
            writer.writeheader()

            # 写入数据行
            for item in new_sites_dict_list:
                writer.writerow(item)

        print(f"数据已成功写入 {csv_file}")
    except FileNotFoundError:
        print(f"文件 {json_file} 未找到")
    except json.JSONDecodeError as e:
        print(f"解析JSON文件时出错: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


# 示例使用
if __name__ == "__main__":
    cur_dir = os.getcwd()
    config_file_path = os.path.join(cur_dir, "intf_config\\tvbox.intf.cfg")
    latest_jar_folder = os.path.join(cur_dir, "..\\jar\\latest")

    print(config_file_path)
    # 替换为你的配置文件路径 
    # file_path = 'config.txt'  
    # 调用解析函数 
    result = parse_config_file(config_file_path)
    # 打印解析结果 
    for item in result:
        # print(item)
        intf_name = ''.join(lazy_pinyin(item[0], style=Style.NORMAL))
        json_file_name = os.path.join(cur_dir, "intf_json", intf_name + ".json")

        json_intf_url = item[1]
        print(json_intf_url)
        content = get_json_content(json_intf_url)
        # print(content)
        if content:
            safe_json_write(content, json_file_name)

        # download default jar to latest path
        print(json_file_name)
        default_jar_url = get_default_jar_url(json_file_name)
        get_jar_from_url(default_jar_url, os.path.join(latest_jar_folder, intf_name + '.jar'))
        #
        #
        # # save to csv
        # sites_csv_file_path = os.path.join(cur_dir, "intf_csv\\merged_sites_intf.csv")
        # lives_csv_file_path = os.path.join(cur_dir, "intf_csv\\merged_lives_intf.csv")
        # parse_json_to_sites_csv(intf_name, json_file_name, sites_csv_file_path)
