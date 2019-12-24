#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from lxml import html
import warnings
from time import sleep
import numpy as np
from scrapy import Selector
import pickle
import pandas as pd
from datetime import datetime
from time import sleep
import json


session = requests.session()

def login(account_name, password):
    post_url = 'https://accounts.douban.com/j/mobile/login/basic'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
    }

    postdata = {
        "ck":"",
        'name': account_name,
        'password': password,
        'rememberme': 'false',
        "ticket":""
    }
        # 不需要验证码直接登录成功
    login_page = session.post(post_url, data=postdata, headers=headers, timeout = 60)
    res_json = json.loads(login_page.text)
    if res_json["status"] == "success":
        print("登录成功")
        with open("douban.cookie", "wb") as f:
            pickle.dump(login_page.cookies, f)
    else:
        print(res_json)
        print("登录失败")


def spider_movie(page_num):
    # 通过查看用户个人信息来判断是否已经登录
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
    }
    user_links = []

    for page in range(page_num):
        print("目前正在获取第: ", str(page))
        url = "https://movie.douban.com/subject/25853071/reviews?start={}".format(page * 20)
        try:
            page = session.get(url, headers=headers, allow_redirects=False, timeout = 30).text
            soup = BeautifulSoup(page, "lxml")
            user_names = soup.select("a.name")
            print("正在获取用户的链接...")
            for user in user_names:
                user_links.append(user["href"])

            sleep(np.random.randint(1, 5))

        except:
            print("网页请求失败")

    with open("用户链接.txt","w") as filehandle:
        for url in user_links:
            filehandle.writelines("%s\n" % url)

    print("保存成功！")
    return user_links



def batch_spider():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
    }
    location = []
    with open("用户链接.txt","r") as filehandler:
        for url_space in filehandler:
            url = url_space[:-1]
            print("现在正在爬取链接：{}".format(url))
            with open("douban.cookie","rb") as f:
                cookies = pickle.load(f)
                try:
                    page = requests.get(url, headers=headers, timeout = 60, cookies = cookies).text
                    # print(page)
                    soup = BeautifulSoup(page, "lxml")
                    user_info = soup.select("div.user-info a")
                    if user_info:
                        for user in user_info:
                            print(user.get_text())
                            location.append(user.get_text())
                            sleep(np.random.randint(1, 3))
                    else:
                        print(soup.select("div.user-info"))
                        sleep(np.random.randint(1, 3))
                except:
                    print("网页获取失败")

                with open("用户地区.txt", "w") as f2:
                    for loc in location:
                        f2.writelines("%s\n" % loc)



def spider_people(page_num):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
    }
    location = []
    for page in range(page_num):
        print("目前正在获取第: 页", str(page))
        url = "https://movie.douban.com/subject/25853071/collections?start={}".format(page * 20)
        print(url)
        page = session.get(url, headers=headers, allow_redirects=False, timeout = 30).text
        soup = BeautifulSoup(page, "lxml")
        user_names = soup.select("tr div.pl2 a")
        # print(user_names)
        print("正在获取用户的信息...")
        for user in user_names:
            try:
                if user.get_text().split("(")[1]:
                    print(user.get_text().split("(")[1].split(")")[0])
                    location.append(user.get_text().split("(")[1].split(")")[0])
            except:
                print("None")
        sleep(np.random.randint(1, 3))

    with open("用户地区.txt", "a") as f3:
        for loc in location:
            f3.writelines("%s\n" % loc)


def get_review(page_num):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
    }
    review_links = []
    for page in range(page_num):
        print("目前正在获取第: 页", str(page))
        url = "https://movie.douban.com/subject/25853071/reviews?start={}".format(page * 20)
        print("现在正在爬取链接：{}".format(url))
        with open("douban.cookie","rb") as f:
            cookies = pickle.load(f)
            page = requests.get(url, headers=headers, timeout = 60, cookies = cookies).text
            # print(page)
            soup = BeautifulSoup(page, "lxml")
            review_lists = soup.select("div.main-bd h2 a")
            # print(review_lists)
            for review in review_lists:
                print(review["href"])
                review_links.append(review["href"])

            sleep(np.random.randint(1, 3))


        with open("评论链接.txt", "w") as filehandle2:
            for url in review_links:
                filehandle2.writelines("%s\n" % url)



def spider_review():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
    }
    contents = []
    with open("评论链接.txt","r") as filehandler:
        for url_space in filehandler:
            url = url_space[:-1]
            print("现在正在爬取链接：{}".format(url))
            # with open("douban.cookie","rb") as f:
            #     cookies = pickle.load(f)
            try:
                page = requests.get(url, headers=headers, timeout = 60).text
                # print(page)
                soup = BeautifulSoup(page, "lxml")
                content_lists = soup.select("div.review-content.clearfix p")
                for content in content_lists:
                    print(content.get_text())
                    contents.append(content.get_text())

            except:
                print("获取网页失败")

            sleep(np.random.randint(1, 5))

            with open("评论集合.txt", "a") as filehandle2:
                for cont in contents:
                    filehandle2.writelines("%s\n" % cont)


if __name__ == '__main__':
    login("15267862911","xjx1072362067")
    # spider_review()
    print("结束")




