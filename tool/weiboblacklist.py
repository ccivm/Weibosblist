from tqdm import tqdm
import time,os
from weibobase import WeiBo
import json
from jsonpath import jsonpath
import requests
# 打开文件并按行读取
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
        # with open('cookie.txt', 'rt', encoding='utf-8') as f:
        #     cookie = f.read().strip()=
        self.infos_return, self.session = self.login(username, password)
        self.blacklist_ids = blacklist_ids
        self.headers = {
            'origin': 'https://weibo.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
            # 'Cookie': cookie
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



if __name__ == "__main__":
    
    blacklist_ids=get_sb_list()

    WB=WeiboBlackList(username='', password='',blacklist_ids=blacklist_ids)
    WB.run()