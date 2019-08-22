import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

a = re.compile(r'</?\w+[^>]*>')
cookies = #参考https://blog.csdn.net/weixin_41666051/article/details/83020519#

def bs_css_parse_movies(html):
    res_list = []
    soup = BeautifulSoup(html, "lxml")
    jobs = BeautifulSoup(html, "lxml").select('div.job-title')  # 岗位名字
    salary = BeautifulSoup(html, "lxml").select('span.red')  # 薪水
    location = BeautifulSoup(html, "lxml").select('div.info-primary > p')  # 地点和要求
    company = BeautifulSoup(html, "lxml").select('div.company-text > h3.name > a')  # 公司名字
    field = BeautifulSoup(html, "lxml").select('div.company-text > p')  # 公司性质
    employee = BeautifulSoup(html, "lxml").select('div.info-publis > h3.name')  # 招聘人员
    time = BeautifulSoup(html, "lxml").select('div.info-publis > p')  # 发布时间
    infos = {
        "岗位名称": [],
        "薪资水平": [],
        "工作地点": [],
        "经验要求": [],
        "学历要求": [],
        "公司名称": [],
        "所在行业": [],
        "融资阶段": [],
        "公司规模": [],
        "招聘者名称": [],
        "招聘者职位": [],
        "发布日期": []
    }
    for i, each in enumerate(jobs):
        location_i = [a.sub("", e) for e in str(location[i]).split('<em class="vline"></em>')]
        field_i = [a.sub("", e) for e in str(field[i]).split('<em class="vline"></em>')]
        employee_i = [a.sub("", e) for e in str(employee[i]).split('<em class="vline"></em>')]
        infos["岗位名称"].append(each.text.strip())
        infos["薪资水平"].append(salary[i].text.strip())
        infos["公司名称"].append(company[i].text.strip())
        infos["发布日期"].append(time[i].text.strip())
        if len(location_i) == 3:
            infos["工作地点"].append(location_i[0].strip())
            infos["经验要求"].append(location_i[1])
            infos["学历要求"].append(location_i[2])
        elif len(location_i) == 4:
            infos["工作地点"].append(location_i[0].strip())
            infos["经验要求"].append(location_i[1] + " * " + location_i[2])
            infos["学历要求"].append(location_i[3])
        else:
            infos["工作地点"].append(location_i[0].strip())
            infos["经验要求"].append("无")
            infos["学历要求"].append(location_i[1])
        if len(field_i) == 2:
            infos["所在行业"].append(field_i[0])
            infos["融资阶段"].append("无")
            infos["公司规模"].append(field_i[1])
        else:
            infos["所在行业"].append(field_i[0])
            infos["融资阶段"].append(field_i[1])
            infos["公司规模"].append(field_i[2])
        if len(employee_i) == 2:
            infos["招聘者名称"].append(employee_i[0])
            infos["招聘者职位"].append(employee_i[1])
        else:
            infos["招聘者名称"].append(employee_i[0])
            infos["招聘者职位"].append("无")
    return infos


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 \
           (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'}

res = {
    "岗位名称": [],
    "薪资水平": [],
    "工作地点": [],
    "经验要求": [],
    "学历要求": [],
    "公司名称": [],
    "所在行业": [],
    "融资阶段": [],
    "公司规模": [],
    "招聘者名称": [],
    "招聘者职位": [],
    "发布日期": []
}
for i in range(1, 11):
    url = 'https://www.zhipin.com/c101010100/?page=' + str(i) + '&ka=page-' + str(i)
    r = requests.get(url, cookies=cookies, headers=headers)
    res_i = bs_css_parse_movies(r.content)
    for k, v in res.items():
        v += res_i[k]
pd.DataFrame(res).to_excel("咨询.xlsx", index=False)
