import json
import requests
from bs4 import BeautifulSoup


def get_page(page):
    url_temp = 'http://temp.163.com/special/00804KVA/cm_guonei_0{}.js'
    return_list = []
    for i in range(page):
        url = url_temp.format(i)
        response = requests.get(url)
        if response.status_code != 200:
            continue
        content = response.text
        _content = formatContent(content)
        result = json.loads(_content)
        return_list.append(result)
    return return_list


def formatContent(content):
    len = content.__len__()
    return content[14:len - 1]


def get_title_url_times(page_data):
    _dict = {}
    for i in page_data:
        for j in i:
            _list = []
            _list.append(j['time'])  # 发布时间
            _list.append(j['docurl'])  # 正文链接
            source, author, body = get_content(j['docurl'])
            _list.append(source)  # 来源
            _list.append(author)  # 作者
            _list.append(body)  # 正文
            _dict[j['title']] = _list
    return _dict


def get_content(url):
    source = ''
    author = ''
    body = ''
    resp = requests.get(url)
    if resp.status_code == 200:
        body = resp.text
        bs4 = BeautifulSoup(body, "lxml")
        source = bs4.find('a', id='ne_article_source').get_text()
        author = bs4.find('span', class_='ep-editor').get_text()
        body = bs4.find('div', class_='post_text').get_text()
    return source, author, body


def save_data(data):
    f = open('news.txt', 'a+', encoding="utf-8")
    str = json.dumps(data, ensure_ascii=False)
    f.write(str)
    f.close()


if __name__ == '__main__':
    page_data = get_page(3)
    _dict_res = get_title_url_times(page_data)
    save_data(_dict_res)
