#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : ***
# @Author  : Lu Junru
# @Site    : 
# @File    : SpideronBaiduBaike.py
# @Software: PyCharm

#Question Description：以任一百度百科词条为起点，爬取一级词条和二级词条的title、主描述部分的字词条、属性、页面html格式数据，相关词条数目不少于5

#Project Design
#存储：用一个字典存一个词条的data，用一个list存全部词条的字典
#爬虫：用beautifulsoup读取url并解析，从summary保存二级链接；其中用一个list存放待读url，用一个list存放当前正在读的url，用一个set存放已读url，每次判断新的url是否在这三个存储结构中，防止重复
#写文件：循环批量写出词条文件

import re #re模块处理正则表达式
import urllib #urlib处理URL
import urlparse #urlparse从url中抽取信息
from bs4 import BeautifulSoup #beautifulsoup处理html

def data_collect(url,soup): #创建存储单个词条的数据
    data={}
    data['URL']=url #词条url
    #词条的title由<h1>...</h1>标签标识，getText()可以获取其中的文字部分
    data['title']=soup.find("dd", class_="lemmaWgt-lemmaTitle-title").find("h1").getText()
    #词条的简介部分由"lemma-summary"属性标识，通过正则去除[1]、[1-2]、空格等不需要的信息
    summary_base=soup.find("div",class_="lemma-summary")
    data['summary']=re.sub('\n','',re.sub('\[\d-\d\]','',re.sub('\[\d\]','',summary_base.getText())))
    #获取basicinfo部分的全部html代码
    basicinfo=soup.find_all("div",class_="basic-info cmn-clearfix")
    for line in basicinfo:
        i=0
        basicinfo2=[] #建立一个list存放最后的basicinfo
        basicinfo_names=line.find_all("dt",class_="basicInfo-item name") #在basicinfo中获取全部basicinfo的项目名称
        basicinfo_value=line.find_all("dd",class_="basicInfo-item value") #在basicinfo中获取全部basicinfo的项目内容
        while i<len(basicinfo_names): #将basicinfo信息串联成一个字符串
            basicinfo_value1=re.sub('\r','',re.sub('\t','',re.sub('\[\d\]','',basicinfo_value[i].getText()))) 
            basicinfo1=basicinfo_names[i].getText()+"("+basicinfo_value1+")"+"\r"
            basicinfo2.append(basicinfo1)
            i=i+1
    data['basicinfo_final']=basicinfo2 #获取全部basicinfo串联成的字符串
    data['HTML']=urllib.urlopen(url).read() #获取页面html格式信息
    summary_base1=soup.find("div",class_="lemma-summary").find_all(target="_blank")
    data['childrenURLcount']=len(summary_base1) #在summary中获取全部二级词表链接个数
    data['childrenURL']=str(summary_base1) #在summary中获取全部二级词表链接
    return data

data_list=list() #创建存储全部词条data的list

urls_new=list() #创建新url list来存放读到而未请求的url
urls_new,s=[],set() #创建set来存放全部被读过的url，为了防止回读
urls_old=list() #创建旧url list来存放正在被读取的url

#设置爬虫入口
url_initial='http://baike.baidu.com/link?url=NVdcSrGGswR38zQ1lb1he_C1VnbXOSeeuRZyUFInDsxZuYXfIyR6Xvt5SIoK2VP_AbfKKhUCnF8k5ZNIcsRGY6fan7uyOqIl52w0OabVs4DlGWKuhs0U48UGGFz3H0sjkMMMK6HyAMLE2RIdd5PZmCXCd678m-COaN9S_AWcrt4G8rdoz2KlME4aCnQosmzC'
urls_new.append(url_initial)

#设置计数器，控制爬取词条数量
count=1
while len(urls_new)>0: #当待读取的url列表中还有未读取的url时，其实这个没啥用，主要是防止出错
    try:
        url=urls_new.pop(0) #取出列表中第一个url作为当前url
        urls_old.append(url) #在old列表中放入当前url，这样就不用再重复读
        print('No.%d:%s'%(count, url)) #打印出当前请求的url，显示进度
        response=urllib.urlopen(url) #解析url
        count=count+1 
        data=response.read() #从获取的url中取得想要的数据
        soup=BeautifulSoup(data,"html.parser") #用soup获取html代码流
        data_list.append(data_collect(url, soup)) #在词表中加入新读取到的词条相关数据
        content=soup.find_all("div",class_="lemma-summary") #在summary中查找想要的二级链接
        for line in content:
            links=line.find_all(target="_blank")
        for link in links:
            incomplete_url=link['href']
            #如果读到的二级url没有在待读的列表、已读列表或当前列表，则加入待读列表
            complete_url=urlparse.urljoin(url, incomplete_url) 
            if complete_url not in urls_new and complete_url not in urls_old and complete_url not in s:
                urls_new.append(complete_url)
                s.add(complete_url)
    except:
        print('读取URL失败')
    if count>1107: #根据用户需求设定请求链接个数
        break

base='/Users/admin1/Desktop/Junru-Lu.百度百科/' #批量导出文件路径的共同部分
for dic in data_list: #批量写出全部读取到的词条
    line='title:%s\nURL:%s\nsummary:%s\nbasicinfo:%s\nHTML:%s\nchildrenURLcount:%d\nchildrenURL:%s\n'%(dic['title'].encode('utf-8'),dic['URL'].encode('utf-8'),dic['summary'].encode('utf-8'),"".join(dic['basicinfo_final']).encode("utf-8"),"".join(dic['HTML']),dic['childrenURLcount'],dic['childrenURL'].encode("utf-8"))
    filename=base+'词条[%s]'%(dic['title'].encode('utf-8'))+'.txt'
    fhand=open(filename, 'w')
    fhand.write(line)
    fhand.write("\n")
    fhand.close()
