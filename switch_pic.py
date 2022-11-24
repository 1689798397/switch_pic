import base64
import glob
import os
import re
import uuid

import requests

config = {
    "proxy": None
}


# 磁盘中的图片转换为base64
def disk_base64(pic_path):
    try:
        with open(pic_path, "rb") as pic_b:
            base64_data = base64.b64encode(pic_b.read())
            base64_str = base64_data.decode()
            pic = "data:image/png;base64,%s" % base64_str
            return "![](" + pic + ")"
    except:
        print(pic_path + " 转化失败！")
        return "![](" + pic_path + ")"


# 网络图片转换为base64
def net_base64(pic_url):
    try:
        proxies = {"http": config["proxy"], "https": config["proxy"]}
        result_data = requests.get(url=pic_url, proxies=proxies).content
        base64_data = base64.b64encode(result_data)
        base64_str = base64_data.decode()
        pic = "data:image/png;base64,%s" % base64_str
        return "![](" + pic + ")"
    except:
        print(pic_url + " 转化失败！")
        return "![](" + pic_url + ")"


# 磁盘图片上传到网络
def disk_net(pic_path):
    url = "http://127.0.0.1:36677/upload"
    pic_list = [pic_path]
    requests_body = {
        "list": pic_list
    }
    result_json = requests.post(url, json=requests_body).json()
    # 判断上传是否成功
    if result_json['success']:
        pic = result_json['result'][0]
        return "![](" + pic + ")"
    else:
        with open("./error.log", "a+", encoding='UTF-8') as f:
            f.write("\n" + pic_path)
        pic = pic_path
        return "![](" + pic + ")"


# base64上传网络
def base64_net(base64str):
    try:
        base64str = base64str.replace("data:image/png;base64,", "")
        url = "http://127.0.0.1:36677/upload"
        with open("D:\\temp.png", "wb") as w:
            w.write(base64.b64decode(base64str))
        pic_list = ["D:\\temp.png"]
        requests_body = {
            "list": pic_list
        }
        result_json = requests.post(url, json=requests_body).json()
        # 判断上传是否成功
        if result_json['success']:
            pic = result_json['result'][0]
            return "![](" + pic + ")"
        else:
            with open("./error.log", "a+", encoding='UTF-8') as f:
                f.write("\n" + base64str)
            pic = base64str
            return "![](" + pic + ")"
    except:
        print(base64str + " 转化失败！")
        return "![](" + base64str + ")"


# 绝对路径转相对路径
def disk_disk(md_dir_path, source_pic):
    try:
        pic_name = str(uuid.uuid4()) + ".png"
        pic = md_dir_path + "/media/" + pic_name
        if not os.path.exists(md_dir_path + "/media"):
            os.makedirs(md_dir_path + "/media")
        with open(source_pic, "rb") as r:
            with open(pic, "wb") as w:
                w.write(r.read())
        return "![](./media/" + pic_name + ")"
    except:
        print(source_pic + " 转化失败！")
        return "![](" + source_pic + ")"


# 网络图片转化为磁盘图片
def net_disk(md_dir_path, pic_url):
    try:
        proxies = {"http": config["proxy"], "https": config["proxy"]}
        pic_data = requests.get(url=pic_url, proxies=proxies).content
        pic_name = str(uuid.uuid4()) + ".png"
        pic = md_dir_path + "/media/" + pic_name
        if not os.path.exists(md_dir_path + "/media"):
            os.makedirs(md_dir_path + "/media")
        with open(pic, "wb") as f:
            f.write(pic_data)
        return "![](./media/" + pic_name + ")"
    except:
        print(pic_url + " 转化失败！")
        return "![](" + pic_url + ")"


# base64转换为磁盘图片
def base64_disk(md_dir_path, base64str):
    try:
        base64str = base64str.replace("data:image/png;base64,", "")
        pic_name = str(uuid.uuid4()) + ".png"
        pic = md_dir_path + "/media/" + pic_name
        if not os.path.exists(md_dir_path + "/media"):
            os.makedirs(md_dir_path + "/media")
        with open(pic, "wb") as f:
            f.write(base64.b64decode(base64str))
        return "![](./media/" + pic_name + ")"
    except:
        print(base64str + " 转化失败！")
        return "![](" + base64str + ")"


# 修改md文件
def read_md(md_absolute_path, target):
    # md所在文件夹名
    md_dirname = os.path.dirname(os.path.abspath(md_absolute_path))
    # md文件绝对路径
    # md_absolute_path = os.path.basename(md_absolute_path)
    md_str = ""
    with open(md_absolute_path, "r", encoding='UTF-8') as f:
        md_str = f.read()
        # 正则匹配所有markdown图片标签
        img_label_list = re.findall(r'!\[.*\]\(.*\)', md_str)
        # 正则匹配所有html图片标签
        html_label_list = re.findall(r'<img.*>?', md_str)
        pic_label_list = img_label_list + html_label_list
        # 遍历图片标签
        for pic_label in pic_label_list:
            pic_path = ""
            # 获取图片路径
            if "![" in pic_label:
                pic_path = re.search(r'\(.*\)', pic_label)
                if pic_path:
                    pic_path = pic_path.group().replace("(", "").replace(")", "")
                else:
                    continue
            elif "<img" in pic_label:
                pic_path = re.search(r'src=\"(.*?)\"', pic_label)
                if pic_path:
                    pic_path = pic_path.group().replace('src="', "").replace('"', "")
                else:
                    continue
            # 新图片地址
            new_pic_label = ""
            # 如果是网络图片
            if "http:" in pic_path or "https:" in pic_path:
                if target == "d":
                    new_pic_label = net_disk(md_dirname, pic_path)
                if target == "b":
                    new_pic_label = net_base64(pic_path)
                if target == "n":
                    new_pic_label = pic_label
            # 如果是base64
            elif "data:image" in pic_path:
                if target == "d":
                    new_pic_label = base64_disk(md_dirname, pic_path)
                if target == "n":
                    new_pic_label = base64_net(pic_path)
                if target == "b":
                    new_pic_label = pic_label
            # 如果是绝对路径
            elif os.path.exists(pic_path):
                if target == "b":
                    new_pic_label = disk_base64(pic_path)
                if target == "n":
                    new_pic_label = disk_net(pic_path)
                if target == "d":
                    new_pic_label = disk_disk(md_dirname, pic_path)
            # 如果是相对路径，拼接得到绝对路径
            elif "./" in pic_path:
                pic_abs_path = md_dirname + (pic_path.replace("./", "/"))
                if target == "b":
                    new_pic_label = disk_base64(pic_abs_path)
                if target == "n":
                    new_pic_label = disk_net(pic_abs_path)
                if target == "d":
                    new_pic_label = pic_label
            else:
                pic_abs_path = md_dirname + "/" + pic_path
                if os.path.exists(pic_abs_path):
                    if target == "b":
                        new_pic_label = disk_base64(pic_abs_path)
                    if target == "n":
                        new_pic_label = disk_net(pic_abs_path)
                    if target == "d":
                        new_pic_label = pic_label
            md_str = md_str.replace(pic_label, new_pic_label)
    with open(md_absolute_path, "w", encoding='UTF-8') as w:
        w.write(md_str)


if __name__ == "__main__":
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            config = eval(f.read())
    else:
        with open("config.json", "w", encoding="utf-8") as f:
            f.write(str(config))
    path = input("请输入包含md文件的路径：")
    while not os.path.exists(path):
        path = input("路径有误请重新输入：")
    target = input("请选择图片存放的位置\n\tn:上传到网络\n\td:存放到相对路径\n\tb:转换为base64\n请输入：")
    select_list = ["b", "d", "n"]
    while target not in select_list:
        target = input("存放位置有误请重新输入：")
    for filename in glob.glob(path + r'\**\*.md', recursive=True):
        print(filename + "转化中")
        read_md(filename, target)
