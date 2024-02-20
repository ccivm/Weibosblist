import sqlite3
from tqdm import tqdm
import time,os
from weibobase import WeiBo
import json
from jsonpath import jsonpath
import requests
# 打开文件并按行读取
import requests

def delete_filtered_user(screen_name):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    })

    cookies = {
     }

    url = 'https://weibo.com/ajax/setting/deleteFilteredUser'
    data = {"screen_name": screen_name}
    headers = {
        'authority': 'weibo.com',
        'method': 'POST',
        'path': '/ajax/setting/deleteFilteredUser',
        'scheme': 'https',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'client-version': 'v2.44.62',
        'origin': 'https://weibo.com',
        'referer': 'https://weibo.com/set/shield?type=user',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'server-version': 'v2024.02.04.1',
        'x-requested-with': 'XMLHttpRequest',
        'x-xsrf-token': 'GEzXfgTjixI83EYcWC9ZdeSs',
    }

    try:
        response = session.post(url, headers=headers, cookies=cookies, json=data)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"



def get_sb_list(output_pwd=r"E:\python\nowork\new_weibo\WeiboSpider\output"):
    returndata=[]
    sb_list_files=os.listdir(output_pwd)
    print(sb_list_files)
    for sb_list_file in sb_list_files:
        if sb_list_file.startswith("tweet_spider_by_keyword"):
            with open(os.path.join(output_pwd,sb_list_file), 'r', encoding='utf-8') as file:
                lines = file.readlines()
                for line in lines:
                    try:
                        data = json.loads(line)
                        tempdata=jsonpath(data,"$.user._id")
                        if tempdata:
                            # print("User ID:", tempdata[0])
                            returndata.append(tempdata[0])


                    except json.JSONDecodeError:
                        print("Failed to parse JSON in line:", line)
    return returndata
class WeiboBlackList():
    
    def __init__(self, username, password, blacklist_ids):
        with open('/root/Weibosblist/weibospider/cookie.txt', 'rt', encoding='utf-8') as f:
            cookie = f.read().strip()

        session = requests.Session()

        self.session=session
        # self.infos_return, self.session = self.login(username, password)
        self.blacklist_ids = blacklist_ids
        self.headers = {
            'origin': 'https://weibo.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
            'Cookie': cookie
        }
    '''运行'''
    def run(self):
        url = 'https://weibo.com/aj/filter/block?ajwvr=6'
        pbar = tqdm(self.blacklist_ids)
        for uid in pbar:
            if not uid: continue
            pbar.set_description(f'正在处理用户{uid}')
            data = {
                'uid': uid,
                'filter_type': '1',
                'status': '1',
                'interact': '1',
                'follow': '1',
            }
            self.headers['referer'] = f'http://weibo.com/u/{uid}'
            response = self.session.post(url, data=data, headers=self.headers)
            time.sleep(10)
            try:
                if response.json()['code'] != '100000':
                    self.logging(f'拉黑用户{uid}失败, 原因为{response.json()["msg"]}')
            except requests.exceptions.JSONDecodeError:
                    self.logging(response.text)
                    continue
    '''模拟登录'''
    def login(self, username, password):

        weibo = WeiBo()
        session, infos_return = weibo.login(username=username, password=password,mode='scanqr')
        return session, infos_return
    '''logging'''
    def logging(self, msg, tip='INFO'):
        print(f'[{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} {tip}]: {msg}')
    

    def getFilteredUsers(self):
        # 连接到 SQLite 数据库（如果不存在则会被创建）
        conn = sqlite3.connect('filtered_users.db')
        cursor = conn.cursor()
        # 创建一个表格来存储数据
        cursor.execute('''CREATE TABLE IF NOT EXISTS filtered_users
                        (page INTEGER, card_type INTEGER, scheme TEXT, pic TEXT, title_sub TEXT, desc1 TEXT, itemid TEXT)''')

        for i in range(1, 400):
            response = self.session.get(f"https://weibo.com/ajax/setting/getFilteredUsers?page={i}", headers=self.headers)
            if response.status_code == 200:
                # print(response.json())
                if response.json()["card_group"].__len__()!= 0:
                    card_group = response.json()["card_group"]
                    print(card_group)
                    for card in card_group:
                        cursor.execute("INSERT INTO filtered_users (page, card_type, scheme, pic, title_sub, desc1, itemid) VALUES (?, ?, ?, ?, ?, ?, ?)",
                                    (i, card["card_type"], card["scheme"], card["pic"], card["title_sub"], card["desc1"], card["itemid"]))
                    conn.commit()
                    time.sleep(3)
                    print(f"第{i}页")
                else:
                    print("获取完毕")
                    break


        conn.close()

    def deleteFilteredUser(self):

        conn = sqlite3.connect('filtered_users.db')
        cursor = conn.cursor()


        cursor.execute("SELECT title_sub FROM filtered_users")
        users = cursor.fetchall()

        for user in users:

            cursor.execute("DELETE FROM filtered_users WHERE title_sub=?", (user[0],))
            conn.commit()
            result = delete_filtered_user(user[0])
            # print(result)
            print(f"已删除用户：{user[0]}")
            time.sleep(1)

        # 关闭连接
        conn.close()

                        

           


if __name__ == "__main__":
    


    WB=WeiboBlackList(username='', password='',blacklist_ids="")
    WB.getFilteredUsers()
    WB.deleteFilteredUser()
    