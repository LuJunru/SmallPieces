import requests
from bs4 import BeautifulSoup
from settings import COOKIE
import pickle


def bs_css_parse_movies(html, j):
    res_list = []
    soup = BeautifulSoup(html, "lxml")
    div_list = soup.select("tbody > tr > th > a")
    time_list = soup.select("tbody > tr > td.by > em")
    page_list = soup.select("tbody > tr > th > span.tps > a")
    page_dict = {}
    for page in page_list:
        page_dict['http://bbs.yingjiesheng.com/thread-' + page["href"].split("-")[1] + 
                  "-1-" + str(j) + ".html"] = page.text.strip()
    for i, each in enumerate(div_list):
        url = 'http:' + each["href"]
        res_list.append({'url': url,
                         'created_time': time_list[2 * i].text.strip(),
                         'last_time_reply': time_list[2 * i + 1].text.strip(),
                         'page': page_dict.get('http:' + each["href"], 1)})
    return res_list


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 \
           (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
cookies = COOKIE

res = []
for i in range(1, 48):
    url = 'http://bbs.yingjiesheng.com/forum-683-' + str(i) + '.html'
    r = requests.get(url, cookies=cookies, headers=headers)
    c = bs_css_parse_movies(r.content, i)
    res += c
with open('urls.pk', 'wb') as f:
    pickle.dump(res, f)
with open('urls.pk', 'rb') as f:
    print(pickle.load(f))
