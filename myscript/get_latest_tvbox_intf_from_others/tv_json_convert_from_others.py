import os
import sys
# from PyQt5 import QtWidgets
import json 
from pathlib import Path 
from datetime import datetime 
import hashlib

def find_json_files(folder_path):
    """查找指定文件夹下所有JSON文件"""
    return list(Path(folder_path).rglob("*.json"))

def get_src_name_from_json_file_path(json_file_path):
    p = Path(json_file_path)
    return p.stem.split('.')[0]

def get_src_date_from_json_file_path(json_file_path):
    p = Path(json_file_path)
    return p.stem.split('.')[1]

def extract_field(json_file, target_field):
    """从JSON文件中提取指定一个字段"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get(target_field)
    except Exception as e:
        print(f"处理文件 {json_file} 出错: {e}")
        return None

def file_to_md5(file_path):
    """计算文件的MD5哈希值并返回16进制字符串"""
    with open(file_path, 'rb') as f:
        md5_hash = hashlib.md5() 
        for chunk in iter(lambda: f.read(4096),  b''):
            md5_hash.update(chunk) 
    return md5_hash.hexdigest()   # 返回32位小写16进制字符串 
    
if __name__ == '__main__':
    # app = QtWidgets.QApplication(sys.argv)  # 初始化界面
    # MainWindow = QtWidgets.QWidget()  # 生成一个主窗口
    # MainWindow.show()  # 显示主窗口
    # sys.exit(app.exec_())  # 在主线程中退出

    # 1. 指定一个文件夹，从里面找出来所有json文件；
    # 2. 提取这些json文件中的"spider"字段和另外一个文件夹中的.jar文件进行匹配；
    # 3. 提取这些json文件中的"sites"字段，进行合并，合并为一个新的json文件；
    cur_dir = os.getcwd()
    target_folder = os.path.join(cur_dir, ".\\intf_json\\")
    json_files = find_json_files(target_folder)
    github_repo_path = 'https://gh-proxy.com/https://raw.githubusercontent.com/LuckySflr/tvjson/refs/heads/src/'
    print(json_files)
    print("\n---------------------\n")
    
    all_site_list = []
    for file in json_files:
        src_from = get_src_name_from_json_file_path(file)
        src_date = get_src_date_from_json_file_path(file)
        spider_jar_path = os.path.join(cur_dir, ".\\intf_spider_jar\\" + src_date + "\\" + src_from + ".jar")
        spider_jar_md5 = file_to_md5(spider_jar_path)
        http_jar_path = github_repo_path + "myscript/get_latest_tvbox_intf_from_others/intf_spider_jar/" + src_date + '/' + src_from + '.jar'
        http_jar_path += ';md5;' + str(spider_jar_md5)

        target_field = 'sites'
        sites_list = extract_field(file, target_field)
        for site in sites_list:
            if ('jar' not in site) and (site.get('api').startswith('csp_')):
                site['jar'] = http_jar_path
            site['src_from'] = src_from
            all_site_list.append(site)
    my_new_site_json_dict = dict()
    my_new_site_json_dict['sites'] = all_site_list

    
    with open(os.path.join(cur_dir, "my.new_merged.json"), 'w',  encoding='utf-8') as f:
        json.dump(my_new_site_json_dict, f, indent=2, ensure_ascii=False)

