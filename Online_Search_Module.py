# -*- coding: utf-8 -*-
# @Author  : Junru_Lu
# @File    : Online_Search_Module.py
# @Software: PyCharm
# @Environment : Python 3.6+

# 网页和服务请求相关包
from bs4 import BeautifulSoup
from urllib.parse import quote
import requests

# 基础包
import re
import jieba
from functools import reduce
import operator

# 编码相关包
import importlib, sys
importlib.reload(sys)

'''
本配置文件用于测试和编写在线搜索模块

定义说明：
新问题：用户使用本系统时输入的信息
候选问题：使用ES检索到的与新问题相同/相似的问题，候选问题可能相同
候选答案：每个候选问题有一个对应的答案，本地库中数据以问题-答案对形式存放
'''

# ------------------预加载------------------ #


stopwords = set(list(open('basic_files/stopwords.txt', 'r').read().strip().split('\n')))  # 停用词表
photo_content = {}  # 百度知道上图片-文字对应表，目前共99个文字
for content_line in open('basic_files/photo_content.txt', 'r'):
    content = content_line.strip().split('\t')[1]
    photo_content[content] = content_line.strip().split('\t')[0]


# ------------------基础函数------------------ #


def TNL(inputs):  # 返回输入句子的NER
    url = 'http://172.18.1.85:2033/ner'
    tem = {'text': inputs}
    r = requests.post(url, data=tem)
    ner_list = [jieba.lcut(w.split('/')[0]) for w in
                list(filter(lambda e: ('/O' not in e) and (e != ''), list(r.text.split(': "')[1][:-2].split(' '))))]
    if len(ner_list) > 0:
        return reduce(operator.add, ner_list)
    else:
        return ner_list


def TMC(input):
    return [s for s in jieba.lcut(input) if s not in stopwords]


# ------------------在线搜索模块------------------ #


def get_html(url):  # 模拟代理请求和下载html
    headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686)Gecko/20071127 Firefox/2.0.0.11'}
    soup = BeautifulSoup(requests.get(url=url, headers=headers).content, "lxml")
    return soup


class OnlineSearch:  # 在线搜索：先在百度主页面上搜索，搜不到再到百度知道上搜索
    def __init__(self, text):
        self.content = text
        self.content1 = re.sub('天气', 'tianqi', self.content)
        self.main_url = 'https://www.baidu.com/s?wd=' + quote(self.content1)  # 百度知道上搜索的url请求
        self.main_soup = get_html(self.main_url)  # 百度主页面搜索结果返回的html

    def Baidu_Search(self):

        answer = {}
        try:
            result = self.main_soup.find(id=1)  # 获取html中第一个搜索结果
            d = result.attrs  # 检验搜索结果是否为空
        except:
            answer['qaflag'] = "请给我一首歌的时间,我去找人问问..."  # 无搜索结果时返回安全回答
            return answer

        if result.attrs.get('mu'):  # 检测搜索结果是否为百度知识图谱
            r = result.find(class_='op_exactqa_s_answer')
            if r is not None:
                answer['qaflag'] = r.get_text().strip().replace("\n", "").replace(" ", "")
                return answer

        if result.attrs.get('mu') and \
                result.attrs['mu'].__contains__('http://open.baidu.com/static/calculator/calculator.html'):
            # 检测搜索结果是否为百度计算器
            r = result.find(class_='op_new_val_screen_result')
            if r is not None:
                answer['qaflag'] = r.get_text().strip().replace("\xa0", "").replace(" ", "").replace("\n", "")
                return answer

        if result.attrs.get('tpl') and result.attrs['tpl'].__contains__('calendar'):
            # 检测搜索结果是否为日期(万年历)
            r = result.find(class_='op-calendar-content')
            if r is not None:
                answer['qaflag'] = ''.join(re.compile('[\u4e00-\u9fa50-9\t]').
                    findall(re.sub('\s', '', str(r)).replace('</span>', '\t').replace('<span>', ''))[:-1])
                return answer

        try:
            result2 = self.main_soup.find(id=2)  # 获取html中第二个搜索结果
            d2 = result2.attrs  # 检验搜索结果是否为空
        except:
            result2 = '不存在'

        if result2 != '不存在':
            if result2.attrs.get('tpl') and result2.attrs['tpl'].__contains__('calendar'):
                # 检测搜索结果是否为日期(万年历)
                r = result2.find(class_='op-calendar-content')
                if r is not None:
                    answer['qaflag'] = ''.join(re.compile('[\u4e00-\u9fa50-9\t]').\
                        findall(re.sub('\s', '', str(r)).replace('</span>', '\t').replace('<span>', ''))[:-1])
                    return answer

        if result.attrs.get('tpl') and "time" in result.attrs['tpl'] and "weather" not in result.attrs['tpl'] \
                and "news" not in result.attrs['tpl'] and "realtime" not in result.attrs['tpl']:
            # 检测搜索结果是否为日期或时间
            sublink = result.attrs['mu']
            if sublink == 'http://time.tianqi.com/':
                sublink = 'http://time.tianqi.com/beijing'
            r = get_html(sublink).find(class_='time').get_text()
            if r is not None:
                answer['qaflag'] = r
                return answer

        if result.attrs.get('mu'):  # 检测搜索结果是否为百度天气
            r = result.find(class_='op_weather4_twoicon_today OP_LOG_LINK')
            if r is not None:
                answer['qaflag'] = r.get_text().strip().replace("\n", "").replace(" ", "").replace('\xa0', '\n')
                return answer

        if result.attrs.get('tpl') and 'sp_fanyi' in result.attrs['tpl']:
            r = result.find(class_='op_sp_fanyi_line_two')
            if r is not None:
                answer['qaflag'] = r.get_text().strip()
                return answer

        if result.find("h3") is not None and result.find("h3").find("a").get_text().__contains__(u"百度百科"):
            # 检测搜索结果是否为百度百科
            url = result.find("h3").find("a")['href']
            if url is not None:
                baike_soup = get_html(url)  # 获取百度百科链接，进入百科，获取百科标题与摘要部分
                r1 = baike_soup.find(class_='lemma-summary')
                if r1 is not None:
                    r1 = r1.get_text().replace("\n", "").strip()
                    answer['qaflag'] = r1
                    return answer

        if len(answer) == 0:  # 当百度主页面的第一条检索结果未能被上述条件捕获时，请求百度知道检索

            text_main_content = TMC(self.content)
            text_ner_list = TNL(self.content)
            search_list = text_ner_list + text_main_content
            sl = self.content + " ".join(search_list)
            zhidao_url = "https://zhidao.baidu.com/search?word=" + quote(sl)  # 百度主页面搜索的url请求

            zhidao_soup = get_html(zhidao_url)
            try:  # 一种情况是百度知道返回的搜索结果链接到了百度百科
                subsoup = get_html(zhidao_soup.find(class_='wgt-baike mb-20').find('a', href=True)['href'])
                r1 = subsoup.find(class_='lemma-summary')
                if r1 is not None:
                    r1 = r1.get_text().replace("\n", "").strip()
                    answer['qaflag'] = r1
                    return answer
            except:
                try:  # 另一种情况是获取百度知道搜索结果中前三条带有最佳回答/推荐回答的问答
                    subsoups = [get_html(subsoup.find('a', href=True)['href']) for subsoup in zhidao_soup.find_all(class_='dt mb-8')]
                    if len(subsoups) == 0:
                        subsoups = [get_html(subsoup.find('a', href=True)['href']) for subsoup in zhidao_soup.find_all(class_='dt mb-4 line')[0:3]]
                    p = 0
                    for subsoup in subsoups:
                        try:  # 在问答页面中，获取最佳回答，并解决文字以图片形式呈现和答案换行消失的问题
                            qtitle = subsoup.find(class_='ask-title').get_text().strip()
                            ans = subsoup.find(class_='bd answer').find('pre')
                            if ans is None:
                                ans = subsoup.find(class_='bd answer').find('ul')
                            if ans is None:
                                ans = subsoup.find(class_='bd answer').find('ol')
                            anss = re.sub("<br/>", "\n", str(ans))
                            anss = re.sub("<br>", "\n", anss)
                            anss = re.sub("<p/>", "\n", anss)
                            anss = re.sub("<p>", "\n", anss)
                            anss = re.sub("<li>", "·", anss)
                            anss = re.sub("·\n", "·", anss)
                            anss = re.sub("</li>", "\n", anss)
                            anss = re.sub("\n+", "\n", anss)
                            anss_list = [el.strip().split('"')[0] for el in re.findall(r'[a-zA-z]+://[^\s]*', anss)]
                            for eln in anss_list:
                                if photo_content.get(eln) is not None:
                                    ansss = anss.replace(eln, photo_content[eln])
                                    anss = ansss
                            anss = re.sub('<img class="word-replace" src="', '', anss).replace('"/>', '')
                            bdans = BeautifulSoup(anss, 'lxml').get_text().replace('\u3000', '')
                            if bdans != 'None':
                                answer['Top-' + str(p + 1)] = qtitle + "||" + bdans
                            p += 1
                        except:
                            pass
                except:
                    pass

        if len(answer) == 0:  # 实时搜索未能获取答案，返回安全回答
            answer['qaflag'] = "请给我一首歌的时间,我去找人问问..."

        return answer


# ------------------主函数------------------ #


if __name__ == '__main__':  # 供测试时使用

    while True:

        s1 = input("请输入查询的内容：")
        OS = OnlineSearch(s1)
        tub = OS.Baidu_Search()
        for tu in tub:
            print(tu, tub[tu])

    pass