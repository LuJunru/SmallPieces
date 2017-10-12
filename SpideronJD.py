#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/15 16:18
# @Author  : Lu Junru
# @Site    : 
# @File    : SpideronJD.py
# @Software: PyCharm

#Question Description：获取京东某一商品词条下所有商品：名称 价格 详情（商品介绍）评价页的前五页

#Project Design
#存储：1.用一个字典存一个商品的data；2.用一个list存放全部商品信息
#爬虫：1.用selenium模拟翻页，用beautifulsoup读取商品清单(商品名称、url、价格)，并将商品url存在一个list中；2.依次读入每个商品的url，用beautifulsoup读取url并解析，获取商品详情及前5页评论
#写文件：1.写出商品清单；2.循环批量写出每个商品信息

from selenium import webdriver
import time  #调入time函数
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import requests,json
import sys
import urllib
from matplotlib.cbook import Null
reload(sys)
sys.setdefaultencoding('utf-8')

def data_collect(url,name,price): #存储单个商品的信息
    data={}
    data['URL']=url #词条url
    data['name']=name
    data['price']=price
    #商品详情介绍爬取
    soup=BeautifulSoup(urllib.urlopen(url),"html.parser")
    gooddetails2=[]
    try:
        gooddetails=soup.find('ul',class_='parameter2 p-parameter-list').find_all("li")
    except:
        gooddetails=soup.find('ul',class_='p-parameter-list').find_all("li")
    id=0
    for line in gooddetails:
        detail=line.getText()+"\r"
        if '商品编码' in line.getText():
            id=int(re.sub(u"商品编码：","",line.getText()))
        if '商品编号' in line.getText():
            id=int(re.sub(u"商品编号：","",line.getText()))
        gooddetails2.append(detail)
    data['details']=gooddetails2
    #爬评论
    goodcomments=''
    s=requests.session()
    url1='https://club.jd.com/comment/productPageComments.action'
    data1={    
        'callback':'fetchJSON_comment98vv61',
        'productId':id,
        'score':0,
        'sortType':5,
        'pageSize':10,
        'isShadowSku':0,
        'page':0
        }
    while data1['page']<=5:
        t=s.get(url1,params = data1).text
        try:
            t=re.search(r'(?<=fetchJSON_comment98vv61\().*(?=\);)',t).group(0)
        except Exception as e:
            break
        j=json.loads(t)
        commentSummary=j['comments']
        for comment in commentSummary:
            c_content=comment['content']
            c_name=comment['nickname']
            goodcomment=c_name+':'+c_content+'\n'
            goodcomments=goodcomments+goodcomment
        data1['page']+=1
    data['comment']=goodcomments
    return data
driver=webdriver.Chrome(executable_path="/usr/local/bin/chromedriver") 
driver.get('https://www.jd.com/?cu=true&utm_source=baidu-pinzhuan&utm_medium=cpc&utm_campaign=t_288551095_baidupinzhuan&utm_term=0f3d30c8dba7459bb52f2eb5eba8ac7d_0_2d072791bfb14f4a95a6c2717dd8c462') #访问登录页面
#str=raw_input("请输入要检索的商品: ") 从键盘输入未解决
time.sleep(3)
driver.find_element_by_id('key').send_keys(u'党章字帖') #定位用户输入框并输入
ActionChains(driver).key_down(Keys.ENTER).perform()
time.sleep(5) #加载延时
data={} #data里面存商品清单：goodnameURL为“商品名称及url”；url就是商品的url，用来下一步查找
dataurl=[] #储存商品url
goodList=[] #存商品名称及url
goodnames=[] #存商品名称
goodPrice=[] #存商品价格
soup=BeautifulSoup(driver.page_source,"html.parser") #用soup获取搜索页面html
s=0 #因为商品集合在一个txt中，所以需要一个标号s
#爬取商品名称及url
page=1
while (soup.find(class_='pn-next').find('em').getText().encode('utf-8')=='下一页')==True: #直到没有下一页为止
    time.sleep(3)
    driver.execute_script("window.scrollBy(100,5000)")
    time.sleep(3)
    driver.execute_script("window.scrollBy(100,5000)")
    time.sleep(3)
    soup=BeautifulSoup(driver.page_source,"html.parser") #用soup获取当前页面的html码流
    goodslist=soup.find('ul',class_='gl-warp clearfix').find_all(class_="p-name p-name-type-2")
    i=0
    while i<len(goodslist):
        goodnameURL=goodslist[i].find('a',target='_blank')
        for line in goodnameURL: #获取商品名称及url
            if 'https:' in goodnameURL.get('href'):
                goodnameurl=goodnameURL.get('href')
            else:
                goodnameurl='https:'+goodnameURL.get('href')
        if goodnameurl not in dataurl:
            goodname=re.sub('\n','',goodslist[i].find('em').getText())
            goodprice=re.sub('\n','',soup.find('ul',class_='gl-warp clearfix').find_all(class_="p-price")[i].getText())
            goodnameURL2="No."+str(s+1)+" "+goodname+":"+goodnameurl
            goodnames.append(goodname)
            goodList.append(goodnameURL2)
            goodPrice.append(goodprice)
            dataurl.append(goodnameurl)
        i=i+1
        s=s+1
    driver.find_element_by_class_name("pn-next").click() #完成当前页面的信息收集后进入下一页
    if (soup.find(class_='pn-next disabled')):
        break
    #if page>=5: #如果被搜索的关键词下有很多商品，可以只爬到前几页
        #break
data['goodnameURL']=goodList
time.sleep(2)
driver.close()
time.sleep(2)
filename='/Users/admin1/Desktop/Junru-Lu.JD/商品目录.txt'
j=0
fhand=open(filename, 'w')
while j<len(data['goodnameURL']):
    line=data['goodnameURL'][j].encode('utf-8')+'\n'
    fhand.write(line)
    j=j+1
fhand.close()
#输出商品页内容
data_list=list()
t=0
while t<len(dataurl):
    url=dataurl[t]
    print 'No.'+str(t+1)+':'+url
    name=goodnames[t]
    price=goodPrice[t]
    data_list.append(data_collect(url,name,price))
    t=t+1
    #if t>=10: #控制输出的具体商品数量
        #break
base='/Users/admin1/Desktop/Junru-Lu.京东/' #批量导出文件路径的共同部分
k=1
for dic in data_list:
    line='URL:%s\nname:%s\nprice:%s\ndetails:%s\ncomment:%s\n'%(dic['URL'].encode('utf-8'),dic['name'].encode('utf-8'),dic['price'].encode('utf-8'),"".join(dic['details']).encode("utf-8"),"".join(dic['comment']).encode("utf-8"))
    filename=base+'No.'+str(k)+'.txt'
    fhand=open(filename, 'w')
    fhand.write(line)
    fhand.write("\n")
    fhand.close()
    k=k+1