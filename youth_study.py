#coding:utf-8
import json
import requests
import re
import pathlib
data_path = "./youth.json"
# 获取accessToken
#appid ,callback, sign可以自己抓包获得，此后可以不变，
def get_access_token(openid):
    get_token_url = "https://qcsh.h5yunban.com/youth-learning/cgi-bin/login/we-chat/callback"
    get_token_params = {
        'callback': 'https%3A%2F%2Fqcsh.h5yunban.com%2Fyouth-learning%2Fmine.php',
        'appid': 'wxa693f4127cc93fad',
        'openid': "",  # 用户的openid，必要的参数
        'sign': 'A5760FCD10C2BD935404F11B95261287',
    }
    get_token_params["openid"] = openid
    response = requests.get(get_token_url,params=get_token_params)
    access_token = re.findall(
        "\('accessToken', '(.*?)'\)", response.text, re.S)[0]
    return access_token


# 获取最新课程
def get_course(access_token):
    course_url = "https://qcsh.h5yunban.com/youth-learning/cgi-bin/common-api/course/current?accessToken="+access_token
    response = requests.get(course_url)
    return {"course": response.json().get("result").get("id")}


# 获取团组织信息
def get_group(access_token,oppenid,group_data):
    if group_data.get(oppenid)==None :#如果groupdata中没有找到oppenid对应的数据，就重新获取
        group_url = "https://qcsh.h5yunban.com/youth-learning/cgi-bin/user-api/course/last-info?accessToken="+access_token
        response = requests.get(group_url)
        data = response.json().get("result")
        nid = data.get("nid")
        card_no = data.get("cardNo")
        sub_org = data.get("subOrg")
        group_data[oppenid] = {"nid": nid, "cardNo": card_no, "subOrg": sub_org}
    return group_data[oppenid]

        
# 决定是否学习
def learning(openid,course,group_data):
    access_token = get_access_token(openid)
    learnin_url = "https://qcsh.h5yunban.com/youth-learning/cgi-bin/user-api/course/join?accessToken="+access_token
    data = get_group(access_token,openid,group_data)#获取团组织信息
    data.update(course)#更新课程编号
    response = requests.post(learnin_url,json=data)
    print(response.text)

def main():
    group_data={}
    course = {}
    #如果文件存在，从本地数据中读取缓存的用户信息
    if pathlib.Path(data_path).exists():
        with open(data_path, "rb") as f:
            group_data = json.load(f)
    origin_group_data =group_data
    openid_list = list(group_data.keys())
    #如果没有用户就直接停止
    if len(openid_list)==0:
        return
    #先获取一个课程编号，后面没必要每次获取
    first_token = get_access_token(openid_list[0])
    course = get_course(first_token)
    for openid in openid_list:
        learning(openid,course,group_data)
    #如果数据更改则重新写入更新数据
    if origin_group_data!=group_data:
        with open(data_path, "w") as f:
            f.write(json.dumps(group_data, indent=4))
main()

#后面是青年大学习完成图片的下载，如果需要可以自行更改下载路径下载
def download_end_img(img_url):
    img_path = "C:/Users/26335/Desktop/end.jpg"
    end_img = requests.get(img_url)
    with open(img_path,"wb") as f:
        f.write(end_img.content)

def get_end_img_url(openid):
    access_token = get_access_token(openid)
    course_url = "https://qcsh.h5yunban.com/youth-learning/cgi-bin/common-api/course/current?accessToken="+access_token
    response = requests.get(course_url)
    path_list = response.json().get("result").get("uri").split("/")
    path_list[-1] = "images"
    path_list.append("end.jpg")
    img_url="/".join(path_list)#拼接图片url
    return img_url
# 用法如下
# download_end_img(get_end_img_url("openid"))
