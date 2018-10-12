import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import csv
import time
import threading
import queue

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

# 分割为五个list
def cut_list(lists):
    task1 = []
    task2 = []
    task3 = []
    task4 = []
    task5 = []
    task1 = lists[0:10]
    task2 = lists[10:20]
    task3 = lists[20:30]
    task4 = lists[30:40]
    task5 = lists[40:50]
    return task1, task2, task3, task4, task5


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
    exit()


def req_page(list):
    for url in list:
        resp = requests.get(url)
        html = resp.text
        task_html.put(html)
        time.sleep(1)


def get_content():
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
        except queue.Empty:
            continue


def look():
    time.sleep(5)
    if task_html.qsize() == 0:
        sort_list = _sort(task_res)
        save(sort_list)



if __name__ == '__main__':
    url_list = make_url(50)
    task1, task2, task3, task4, task5 = cut_list(url_list)
    # 下载好的html队列
    task_html = queue.Queue()
    # 最终结果列表
    task_res = []

    # 获取html线程1
    t1 = threading.Thread(target=req_page, args=(task1,), name='reqThread1')
    # 获取html线程2
    t2 = threading.Thread(target=req_page, args=(task2,), name='reqThread2')
    # 获取html线程3
    t3 = threading.Thread(target=req_page, args=(task3,), name='reqThread3')
    # 获取html线程4
    t4 = threading.Thread(target=req_page, args=(task4,), name='reqThread4')
    # 获取html线程5
    t5 = threading.Thread(target=req_page, args=(task5,), name='reqThread5')

    # 解析html线程
    t6 = threading.Thread(target=get_content, name='getContentThread')
    # 监测线程
    t7 = threading.Thread(target=look, name='look')

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()
