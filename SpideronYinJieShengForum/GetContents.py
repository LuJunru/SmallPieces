import requests
from bs4 import BeautifulSoup
from settings import COOKIE
import pickle


def bs_css_parse_movies(html):
    res_list = []
    soup = BeautifulSoup(html, "lxml")
    div_list = soup.select("td.t_f")
    try:  # some posts are labelled while some are not
        title = soup.select("h1.ts > a")[1].text
    except:
        title = soup.select("h1.ts > a")[0].text
    for each in div_list:
        if each.select("div.quote"):
            each.div.decompose()  # remove quotes
        each_text = each.text.strip()
        if each_text:
            res_list.append(each_text)
    return {'title': title, 'post': res_list}


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 \
           (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}
cookies = COOKIE

with open('urls.pk', 'rb') as f:
    urls = pickle.load(f)
    res = []
    for url in urls:
        c = {"post": []}
        cc = None
        for k in range(1, int(url["page"]) + 1):
            parts = url["url"].split("-")
            r = requests.get(parts[0] + "-" + parts[1] + "-" + str(k) + "-" + parts[3],
                             cookies=cookies, headers=headers)
            cc = bs_css_parse_movies(r.content)
            c["post"] += cc["post"]
        c["title"] = cc["title"]
        c["created_time"] = url["created_time"]
        c["last_time_reply"] = url["last_time_reply"]
        print(url["url"], c["title"])
        res.append(c)
        with open('yingjiesheng.pk', 'wb') as f:
            pickle.dump(res, f)

with open('yingjiesheng.pk', 'rb') as f:
    for e in pickle.load(f):
        print(e["title"])
        print(e["created_time"], e["last_time_reply"])
        print(e["post"])
        print("-" * 40)
