#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/15 16:18
# @Author  : Lu Junru
# @Site    : 
# @File    : SpideronBaiduBaike.py
# @Software: PyCharm

#Project Design
#1.将每一类文本归并到一个txt文件中，按句分行(no.:)，按词分词
#2.建立tf-idf矩阵
#3.计算句子之间的相关度，构建句子相关度矩阵
#4.ranking计算

import jieba                  
import re        
from bs4 import BeautifulSoup

def splitSentence(inputFile, outputFile):  
    fin=open(inputFile, 'r')
    finpage=fin.read()  
    #print finpage
    soup=BeautifulSoup(finpage,"html.parser").find_all("p")
    i=0
    while i<len(soup):
        if soup[i]!="\n":
            soup1=re.sub("\r\n","",soup[i].getText())
        print soup1
        i+=1
    '''
    soup2=re.sub(r"\n",'',soup)
    fout=open(outputFile, 'w')                                  
    for eachLine in soup2:
        if eachLine!='\n': 
            wordList=list(jieba.cut(eachLine))                        #用结巴分词，对每行内容进行分词  
            outStr=''  
            for word in wordList:  
                outStr+=word  
                outStr+='|'  
            fout.write(outStr.strip().encode('utf-8'))    
    print 'Finish！'
    '''  
    fin.close()  
    #fout.close()   
 
splitSentence('inputfile', '/Users/admin1/Desktop/result.txt')