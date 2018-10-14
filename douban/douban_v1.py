import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import csv
import time

# 获取内容
def get(page):
    url = 'https://book.douban.com/tag/%E7%BC%96%E7%A8%8B?start={}&type=T'
    offset = 0
    result = []
    for i in range(page):
        _url = url.format(offset)
        offset += 20
        resp = requests.get(_url)
        if resp.status_code == 200:
            html = resp.text
            if html is not None:
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
                            result.append(list_)
                        except:
                            continue
    time.sleep(1)
    return result


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


if __name__ == '__main__':
    result = get(96)
    sort_list = _sort(result)
    save(sort_list)
