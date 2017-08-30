#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/7/18 11:27
# @Author  : Junru_Lu
# @Site    :
# @File    : Mission1_WithPMI_Complex.py
# @Software: PyCharm

import jieba.analyse
import csv
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time

start = time.clock()
'''
本py包含功能：对topN的生成词，回到文本中查找其相邻窗口为1的词语，组合成新词；再重新利用分词，但将新词作为一个整体，之后计算PMI
，超过一定阈值后保留；最后再抽取tdidf高的词汇
'''
def fun(s):
    d = sorted(s.iteritems(), key=lambda t: t[1], reverse=True)
    return d
#加载自定义词典
jieba.load_userdict("/Users/admin1/Desktop/SmpCup2017/dict_self_withSougou.txt")
#读取带标注的训练集
file_answer='/Users/admin1/Desktop/SmpCup2017/SMPCUP2017任务1训练集/SMPCUP2017_TrainingData_Task1.txt'
f_answer=list(open(file_answer, "r").readlines())
blog_id_answer = [s.strip().split('\001')[0] for s in f_answer]
#对未分词的文件进行关键词提取时使用
contentfile='/Users/admin1/Desktop/SmpCup2017/SMPCUP2017数据集/1_BlogContent.txt'
#生成训练集关键词提取时使用
csvfile=file("/Users/admin1/Desktop/train_pmi_withSougou.csv","w")
writer=csv.writer(csvfile)
writer.writerow(['id','k1','k2','k3'])
#停用词文件
f = open("/Users/admin1/Desktop/SmpCup2017/小朋友词典/self_stopwords_004.txt", "r")
cis = []
for ci in f.readlines():
    cis.append(re.sub("\n", "", ci))
#idf文件
dic={}
for line in open(r'/Users/admin1/Desktop/SmpCup2017/idf_all.txt','r').readlines():
    dic[line.split(' ')[0]]=line.split(' ')[1]
c = open("/Users/admin1/Desktop/SmpCup2017/42topicTo100words.txt", "r")
dicc={}
for line in c:
    L=list(line.strip().split(" "))
    for l in L:
        if dicc.get(l)==None:
            dicc[l]=1
        else:
            dicc[l]=dicc[l]+1
for eachline in open(contentfile,'r'):
    blog_id = eachline.split('\001')[0]
    if blog_id in blog_id_answer:
        print blog_id+":",
        #print "---PMI Result---"
        blog_title = re.sub(" ","",eachline.split('\001')[1].decode("utf-8").lower())
        blog_content = eachline.split('\001')[2].decode("utf-8").lower()
        material=(blog_title+" ")*12+blog_content
        #这个分词结果是对原文本不做任何加工的纯分词结果
        data_list = jieba.lcut(material)
        #去掉空格
        for data in data_list:
            if data==" " or data=="\t":
                data_list.remove(data)
        words_prepare=[]
        words1 = {}
        #提取TOP20作为种子
        for x1,weight1 in jieba.analyse.extract_tags(material, withWeight=True, topK=20, allowPOS=('n')):
                words1[x1] = weight1
        for wo in words1:
            if dic.get(wo)!=None:
                words1[wo]=jieba.lcut(eachline).count(wo)*float(dic[wo])
                words_prepare.append(wo)
        dic_possibleword={}
        w=[]
        flag=0
        for precentword in words_prepare:
            first_pos=0
            precentindexs=[]
            #把precentword在词表中的全部index都找出来
            for i in range(data_list.count(precentword)):
                new_list=data_list[first_pos:]
                next_pos=new_list.index(precentword)+1
                precentindexs.append(first_pos+new_list.index(precentword))
                first_pos+=next_pos
            for precentindex in precentindexs:
                if precentindex==0:
                    backwardword="孟孔明"
                    forwardword=data_list[precentindex + 1]
                if precentindex==len(data_list)-1:
                    backwardword=data_list[precentindex - 1]
                    forwardword="孟孔明"
                else:
                    backwardword = data_list[precentindex - 1]
                    forwardword = data_list[precentindex + 1]
                if dic_possibleword.has_key(precentword) == False and (precentword not in cis) and \
                        (backwardword not in cis) and re.search(u"[a-z0-9\u4e00-\u9fa5]+", backwardword) \
                        and (forwardword not in cis) and re.search(u"[a-z0-9\u4e00-\u9fa5]+", forwardword):
                    p_precentword = float(data_list.count(precentword)) / float(len(data_list))
                    pmi_possibleword = 0.0000000
                    if precentindex == 0:
                        flag = 1
                        possibleword = precentword + forwardword
                        p_forwardword = float(data_list.count(forwardword)) / float(len(data_list))
                        try:
                            jieba.add_word(possibleword)
                            jieba.suggest_freq(possibleword, True)
                            data_list_possible = jieba.lcut(material)
                            jieba.del_word(possibleword)
                            for x in data_list_possible:  # 去掉空格
                                if x == " " or x=="\t":
                                    data_list_possible.remove(x)
                            p_possibleword = float(data_list_possible.count(possibleword)) / float(
                                len(data_list_possible))
                            pmi_possibleword = p_possibleword / (p_forwardword * p_precentword)
                        except:
                            print possibleword,
                    if precentindex != 0 and precentindex != len(data_list) - 1:
                        possibleword1 = backwardword + precentword
                        p_backwardword = float(data_list.count(backwardword)) / float(len(data_list))
                        possibleword2 = precentword + forwardword
                        p_forwardword = float(data_list.count(forwardword)) / float(len(data_list))
                        pmi_possibleword1 = 0.0000000
                        pmi_possibleword2 = 0.0000000
                        try:
                            jieba.add_word(possibleword1)
                            jieba.suggest_freq(possibleword1, True)
                            data_list_possible1 = jieba.lcut(material)
                            jieba.del_word(possibleword1)
                            for x in data_list_possible1:  # 去掉空格
                                if x == " " or x=="\t":
                                    data_list_possible1.remove(x)
                            p_possibleword1 = float(data_list_possible1.count(possibleword1)) / float(
                                len(data_list_possible1))
                            pmi_possibleword1 = p_possibleword1 / (p_backwardword * p_precentword)
                        except:
                            print possibleword1,
                        try:
                            jieba.add_word(possibleword2)
                            jieba.suggest_freq(possibleword2, True)
                            data_list_possible2 = jieba.lcut(material)
                            for x in data_list_possible2:  # 去掉空格
                                if x == " "or x=="\t":
                                    data_list_possible2.remove(x)
                            p_possibleword2 = float(data_list_possible2.count(possibleword2)) / float(
                                len(data_list_possible2))
                            pmi_possibleword2 = p_possibleword2 / (p_backwardword * p_precentword)
                        except:
                            print possibleword2,
                        pmi_possibleword = max(pmi_possibleword1, pmi_possibleword2)
                        if pmi_possibleword == pmi_possibleword1:
                            flag = 2
                            possibleword = possibleword1
                        if pmi_possibleword == pmi_possibleword2:
                            flag = 3
                            possibleword = possibleword2
                    if precentindex == len(data_list) - 1:
                        flag = 4
                        possibleword = backwardword + precentword
                        p_backwardword = float(data_list.count(backwardword)) / float(len(data_list))
                        try:
                            jieba.add_word(possibleword)
                            jieba.suggest_freq(possibleword, True)
                            data_list_possible = jieba.lcut(material)
                            jieba.del_word(possibleword)
                            for x in data_list_possible:  # 去掉空格
                                if x == " " or x=="\t":
                                    data_list_possible.remove(x)
                            p_possibleword = float(data_list_possible.count(possibleword)) / float(
                                len(data_list_possible))
                            pmi_possibleword = p_possibleword / (p_backwardword * p_precentword)
                        except:
                            print possibleword,
                    try:
                        if len(w) == 5 and w[1] == backwardword and flag == (2 or 4):
                            pmi_possibleword = max(pmi_possibleword, w[3])
                            if pmi_possibleword == w[3]:
                                possibleword = w[2]
                            if pmi_possibleword != w[3]:
                                del dic_possibleword[w[2]]
                        if len(w) == 6:
                            if w[1] == backwardword and w[2] == precentword:
                                if flag == w[5]:
                                    pmi_possibleword = max(pmi_possibleword, w[4])
                                    if pmi_possibleword == w[4]:
                                        possibleword = w[3]
                                    if pmi_possibleword != w[4]:
                                        del dic_possibleword[w[3]]
                            if w[2] == backwardword and flag == (2 or 4) and w[5] == 3:
                                pmi_possibleword = max(pmi_possibleword, w[4])
                                if pmi_possibleword == w[4]:
                                    possibleword = w[3]
                                if pmi_possibleword != w[4]:
                                    del dic_possibleword[w[3]]
                    except:
                        print possibleword,
                    w = []  # 存放上一次使用过的三个词，及possibleword、对应pmi、flag
                    w.append(backwardword)
                    w.append(precentword)
                    w.append(forwardword)
                    w.append(possibleword)
                    w.append(pmi_possibleword)
                    w.append(flag)
                    if pmi_possibleword > 60:
                        dic_possibleword[possibleword] = pmi_possibleword
        #print "-"*20
        #print "dic:",
        for key in dic_possibleword:
            try:
                jieba.add_word(key)
                jieba.suggest_freq(key, True)
            except:
                print key,
        s=[]
        words2 = {}
        weights=[]
        s.append(blog_id)
        for x2,weight in jieba.analyse.extract_tags(material, withWeight=True, topK=8, allowPOS=('n')):
                if (x2.encode('utf-8') not in cis) and (x2.encode('utf-8').isdigit()==False) \
                        and (len(x2.encode('utf-8'))>21 and re.match(u"[\u4e00-\u9fa5]", x2))==False:
                    words2[x2] = weight*float(len(x2))
        for word in words2:
            if dic.get(word)!=None and (len(word)>3 and re.match(u"[\u4e00-\u9fa5]", word)):
                words2[word]=jieba.lcut(eachline).count(word)*float(dic[word])
        for key in words2:
            if dicc.get(key)!=None:
                words2[key]=words2[key]*(1.0/float(dicc[key])-1.0/42.0)
            else:
                words2[key]=words2[key]
        for word2 in fun(words2)[0:3]:
            s.append(list(word2)[0])
        writer.writerow(s)
        print ''
f.close()
csvfile.close()
end = time.clock()
print '\n'
print "read: %f s" % (end - start)