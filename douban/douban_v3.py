"""
异步IO
"""
from bs4 import BeautifulSoup
import re
import numpy as np
import csv
import asyncio
import aiohttp
import queue
import time
import threading


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


def get_content(html):
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
                    results.append(list_)
                except:
                    continue


async def get_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                que_html.put(await resp.text())


def look():
    if (que_html.qsize() > 10):
        while True:
            try:
                html = que_html.get(block=False)
                get_content(html)
            except:
                break


def make_task():
    offset = 0
    task = []
    for i in range(50):
        url = 'https://book.douban.com/tag/%E7%BC%96%E7%A8%8B?start={}&type=T'
        # url_ = 'http://localhost'
        url_ = url.format(offset)
        task.append(asyncio.ensure_future(get_html(url_)))
        offset += 20
    return task


if __name__ == '__main__':
    results = []
    que_html = queue.Queue()
    # 生成任务
    tasks = make_task()
    t1 = threading.Thread(target=look)

    # 创建事件循环
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    t1.start()
    t1.join()
    # 主线程排序保存
    save(_sort(results))

