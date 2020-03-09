import requests
import os
import threading
import queue
from lxml import etree
from urllib import request


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


class Producer(threading.Thread):
    def __init__(self, page_queue, image_queue, *args, **kwargs):
        super(Producer, self).__init__(*args,**kwargs)
        self.page_queue = page_queue
        self.image_queue = image_queue

    def run(self) -> None:
        while not self.page_queue.empty():
            page_url = self.page_queue.get()
            location = input(r"""请输入保存的地址,示例：
                    D:\bh3        将文件保存在D盘的bh3文件夹下
                    bh3           在当前目录创建一个bh3文件夹并储存文件
                    current          直接在当前文件夹中储存所有文件
            """)
            if location == "current":
                location = os.getcwd()
            pd = os.path.exists(location)  # 判断输入的地址是否已经存在
            if pd:
                pass
            else:
                try:
                    os.mkdir(location)
                except:
                    print("ERROR: URL illegal！")
                    location = input(r"""请输入保存的地址,示例：
                    D:\bh3        将文件保存在D盘的bh3文件夹下
                    bh3           在当前目录创建一个bh3文件夹并储存文件
                    current          直接在当前文件夹中存储所有文件
                    """)
                    if location == "current":
                        location = os.getcwd()
            try:
                if not os.path.exists(location):
                    os.mkdir(location)
            except:
                print("ERROR: URL illegal！")
                exit()
            dir_path = os.path.join("%s" % location, "%s" % get_title(page_url))  # 生成以漫画题目为标题的文件夹
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)
            log_path = os.path.join("%s" % dir_path, "download.log")              # 生成日志文件路径
            fp = open(log_path, "w")                                              # 清空日志文件中的内容
            fp.close()
            mylog = open(log_path, "a+", encoding='utf-8')                        # 采用追加写入的方式书写日志文件
            print(r"漫画下载中....")
            for x in range(1, page_number(page_url) + 1):
                want_url = "https://comic.bh3.com/book/"+page_url+"/{}/".format(x)
                resp = requests.get(want_url)
                text = resp.content.decode('utf-8')
                html = etree.HTML(text)
                urls = html.xpath('//div/img/@data-original')
                url_number = len(urls)
                for index, url in enumerate(urls):
                    file_location = os.path.join(dir_path, '%d-%d.jpg' % (x, index + 1))
                    self.image_queue.put({"image_url":url, "image_path": file_location})
                    # print(get_title(page_url) + '/%d-%d.jpg' % (x, index + 1) + '已存在！')
                    # mylog.write(get_title(page_url) + '/%d-%d.jpg' % (x, index + 1) + '已存在！\n')
                    # mylog.flush()
            mylog.write("mylog文件正在调试中，敬请期待！\n")
            mylog.flush()
            mylog.close()



class Consumer(threading.Thread):
    def __init__(self,image_queue,*args,**kwargs):
        super(Consumer, self).__init__(*args,**kwargs)
        self.image_queue = image_queue

    def run(self) -> None:
        while True:
            try:
                image_obj = self.image_queue.get()
                image_url = image_obj.get("image_url")
                image_path = image_obj.get("image_path")
                pd_file_path = os.path.isfile(image_path)
                if pd_file_path == False:
                    try:
                        request.urlretrieve(image_url, image_path)
                        print(image_path + "下载完成！")
                    except:
                        print(image_path+"下载失败！")
                else:
                    print(image_path+'已存在！')
            except:
                break


def main():
    page_queue = queue.Queue(20)
    image_queue = queue.Queue(1000)
    print("""
              崩坏3漫画爬虫 v 2.1.0 beta from Sufe.曲水
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
    try:
        while True:
            number = input(r"请输入漫画序号(回车默认1001)：")
            if int(number) >= 1001 and int(number) <= 1021 and int(number) != 1003:
                break
    except:
        number = '1001'
    page_queue.put(number)

    for x in range(5):
        th = Producer(page_queue,image_queue)
        th.start()

    for x in range(10):
        th = Consumer(image_queue)
        th.start()


if __name__ == '__main__':
    main()

# pyinstaller -F D:\\python爬虫\bh3-crawler\bh3-crawler_v2.1.0_beta.py
