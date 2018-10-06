import requests
from bs4 import BeautifulSoup
import re
import numpy as np


def get(page):
    result = []
    for i in range(1):
        _url = url.format(page)
        page += 20
        resp = requests.get(_url)
        if resp.status_code == 200:
            html = resp.text
            bs4 = BeautifulSoup(html, "lxml")
            book_info_list = bs4.find_all('li', class_='subject-item')
            for book_info in book_info_list:
                list_ = []
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
    return result


def _sort(result):
    # 转换成矩阵
    array = np.array(result)
    # 根据矩阵最后一列排序
    sort_arr = array[np.lexsort(array.T)]
    reve_arr = sort_arr[::-1]
    # 转换回list
    sort_list = np.matrix.tolist(reve_arr)
    return sort_list


def save(data):
    f = open('douban.txt', 'a+', encoding="utf-8")




if __name__ == '__main__':
    url = 'https://book.douban.com/tag/%E7%BC%96%E7%A8%8B?start={}&type=T'
    page = 0
    result = get(1)
    sort_list = _sort(result)
    save(sort_list)