import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import csv
import time
import threading
import queue
import traceback
import sys


# 生成分页URL地址
def make_url(page):
    url_list = []
    offset = 0
    for i in range(page):
        url = 'https://book.douban.com/tag/%E7%BC%96%E7%A8%8B?start={}&type=T'
        url_ = url.format(offset)
        url_list.append(url_)
        offset += 20
    return url_list


# 根据评分排序
def _sort(result):
    # 转换成矩阵
    array = np.array(result)
    # 根据矩阵最后一列排序
    sort_arr = array[np.lexsort(array.T)]
    reve_arr = sort_arr[::-1]
    # 转换回list
    sort_list = np.matrix.tolist(reve_arr)
    return sort_list


# 保存到csv
def save(data):
    file_csv = open('douban.csv', 'w+', newline='')
    writer = csv.writer(file_csv)
    header = ['书名', '评论数', '评分']
    writer.writerow(header)
    for book in data:
        try:
            writer.writerow(book)
        except:
            continue
    file_csv.close()
    sys.exit()


def req_page():
    while True:
        try:
            url = url_task.get(block=False)
            resp = requests.get(url)
            html = resp.text
            task_html.put(html)
            time.sleep(1)
        except:
            break

def get_content():
    if task_html.qsize() > 10:
        while True:
            try:
                html = task_html.get(block=False)
                bs4 = BeautifulSoup(html, "lxml")
                book_info_list = bs4.find_all('li', class_='subject-item')
                if book_info_list is not None:
                    for book_info in book_info_list:
                        list_ = []
                        try:
                            star = book_info.find('span', class_='rating_nums').get_text()
                            if float(star) < 9.0:
                                continue
                            title = book_info.find('h2').get_text().replace(' ', '').replace('\n', '')
                            comment = book_info.find('span', class_='pl').get_text()
                            comment = re.sub("\D", "", comment)
                            list_.append(title)
                            list_.append(comment)
                            list_.append(star)
                            task_res.append(list_)
                        except:
                            continue
            except:
                break


if __name__ == '__main__':
    url_list = make_url(50)
    # url 队列
    url_task = queue.Queue()
    for url in url_list:
        url_task.put(url)

    # 下载好的html队列
    task_html = queue.Queue()
    # 最终结果列表
    task_res = []

    threads = []
    # 获取html线程
    for i in range(5):
        threads.append(threading.Thread(target=req_page))

    # 解析html线程
    threads.append(threading.Thread(target=get_content))

    for i in threads:
        i.start()
        i.join()

    save(_sort(task_res))
