import requests
import os
from urllib import request
from lxml import etree
import re


# 作用：能够获取所有书目名称
# 返回：list
# def get_book_title():
#     base_url = "https://comic.bh3.com/book/"
#     resp = requests.get(base_url)
#     text = resp.text
#     text = re.sub(r' | \\n', '', text)
#     book_titles = re.findall(r'''
#         <a href="/book/(.+?)">
#         .+?<div.+?container-title.+?>(.+?)<div.+?>
#     ''', text, re.VERBOSE | re.DOTALL)
#     title_list = []
#     for book in book_titles:
#         title_list.append(book[1].replace('\n', ''))
#     return title_list


# 作用：获取所有书目的序号
# 返回：list
# def get_book_number():
#     base_url = "https://comic.bh3.com/book/"
#     resp = requests.get(base_url)
#     text = resp.text
#     text = re.sub(r' | \\n', '', text)
#     book_titles = re.findall(r'''
#             <a href="/book/(.+?102)">
#             .+?<div.+?container-title.+?>(.+?)<div.+?>
#         ''', text, re.VERBOSE | re.DOTALL)
#     number_list = []
#     for book in book_titles:
#        number_list.append(book[0])
#     return number_list


# 用于获取某个漫画总共有多少话
# 传入参数：漫画的序号
# 返回：int
def page_number(number):
    base_url = "https://comic.bh3.com/book/" + number + "/get_chapter"
    resp = requests.get(base_url)
    text = resp.json()
    total = len(text)
    return total


# 用于得到漫画的题目
# 传入参数：漫画的序号
# 返回：string
def get_title(number):
    base_url = "https://comic.bh3.com/book/" + number + "/"
    resp = requests.get(base_url)
    text = resp.content.decode('utf-8')
    html = etree.HTML(text)
    title = html.xpath('//div[@class="title"]')[0]
    return title.text


# 用于获取每一话的名字
# 传入参数：漫画的序号
# 返回：list
# def get_content(number):
#     base_url = "https://comic.bh3.com/book/"+number+"/get_chapter"
#     resp = requests.get(base_url)
#     result = resp.json()
#     titles = []
#     for every in result:
#         title = every['title']
#         titles.append(title)
#     return titles


def main():
    print("""
            崩坏3漫画爬虫 v 1.2 from Sufe.曲水
        --------------------------------------------
          漫画序号                  标题
            1001                 逃离长空篇
            1002                 樱花追忆篇
            1004                   绀海篇
            1005                   绯樱篇
            1006                 逆熵入侵篇 
            1007                   恩返篇
            1008                   月影篇
            1009                   紫鸢篇
            1010                 神之键秘话
            1011               玩崩坏3的琪亚娜
            1012                  第二次崩坏
            1013                女武神的餐桌
            1014               夏日回忆-预告篇
            1015                  双子：起源
            1016                  双子：入侵
            1017                   蛇之篇
            1018                  雾都假日
            1019                    年岁
            1020                  武装人偶
            1021                    传承
    """)
    number = input("请输入漫画序号：")
    location = input(r"请输入保存的地址(示例：D:\bh3):")
    print("漫画下载中，输入Ctrl+C退出程序....")
    pd = os.path.exists(location)
    if (pd == True):
        pass
    else:
        os.mkdir(location)
    dir_path = os.path.join("%s" % location, "%s" % get_title(number))
    pd_dir_path = os.path.exists(dir_path)
    if (pd_dir_path ==True):
        pass
    else:
        os.mkdir(dir_path)
    for x in range(1, page_number(number)):
        page_url = "https://comic.bh3.com/book/"+number+"/{}/".format(x)
        resp = requests.get(page_url)
        text = resp.content.decode('utf-8')
        html = etree.HTML(text)
        urls = html.xpath('//div/img/@data-original')
        for index, url in enumerate(urls):
            file_location = os.path.join(dir_path, '%d-%d.jpg' % (x, index+1))
            pd_file_path = os.path.isfile(file_location)
            if pd_file_path == False:
                request.urlretrieve(url, file_location)
                print(number+'/%d-%d.jpg' % (x, index+1)+'下载完成！')
            else:
                print(number+'/%d-%d.jpg' % (x, index+1)+'已存在！')


if __name__ == '__main__':
    main()


# pyinstaller -F D:\python爬虫\爬取高清壁纸\爬崩坏3.py
