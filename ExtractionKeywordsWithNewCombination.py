#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/7/18 11:27
# @Author  : Junru_Lu
# @Site    :
# @File    : 1.py
# @Software: PyCharm

import jieba.analyse
import csv
import re
from collections import Counter
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time

'''
本py包含功能：本py包含功能：对topN的生成词进行重新组合，计算新词的tfidf，并将大于现有top3的新词加入到top3中
'''

start=time.clock()
#加载自定义词典
jieba.load_userdict("/Users/admin1/Desktop/SmpCup2017/dict_self_withSougou.txt")
#读取带标注的训练集
file_answer='/Users/admin1/Desktop/SmpCup2017/SMPCUP2017任务1训练集/SMPCUP2017_TrainingData_Task1.txt'
f_answer=list(open(file_answer, "r").readlines())
blog_id_answer = [s.strip().split('\001')[0] for s in f_answer]
#对未分词的文件进行关键词提取时使用
contentfile='/Users/admin1/Desktop/SmpCup2017/SMPCUP2017数据集/1_BlogContent.txt'
#生成训练集关键词提取时使用
csvfile=file("/Users/admin1/Desktop/mission1_result_withSougou.csv","w")
writer=csv.writer(csvfile)
writer.writerow(['id','tfidf'])
#停用词文件
f = open("/Users/admin1/Desktop/SmpCup2017/stopwords.txt", "r")
cis = []
for ci in f.readlines():
    cis.append(re.sub("\n", "", ci))

for eachline in open(contentfile,'r'):
    blog_id = eachline.split('\001')[0]
    if blog_id in blog_id_answer:
        print blog_id+":",
        blog_title = re.sub(" ","",eachline.split('\001')[1].decode("utf-8").lower())
        blog_content = eachline.split('\001')[2].decode("utf-8").lower()
        material=(blog_title+" ")*12+blog_content
        s = []
        words = []
        weights = []
        s.append(blog_id)
        s2 = ''
        for x2, weight in jieba.analyse.extract_tags(material, withWeight=True, topK=20, allowPOS=('n','nt','nz','j')):
            if x2 not in cis:
                words.append(x2)
                weights.append(weight)
        for word1 in words:
            for word2 in words:
                if word1 != word2:
                    word3 = word1 + word2
                    jieba.add_word(word3)
                    jieba.suggest_freq(word3)
                    data = jieba.cut(material)
                    data = dict(Counter(data))
                    jieba.del_word(word3)
                    for k, v in data.items():
                        # 假设idf为10
                        word3_tfidf = v * 10.00 / len(data)
                        if (k == word3) and (word3_tfidf >= weights[2]) and (word3.encode('utf-8').isdigit()==False):
                            print blog_id + ":"
                            print "OldWords:",
                            for word in words:
                                print word,
                            print ''
                            print "OldWeights:",
                            print weights
                            i = 0
                            words_exist = []
                            while i < 2:
                                if (weights[0] < word3_tfidf) and (word3 not in words_exist) and (
                                    word3 not in words[0:3]):
                                    words.insert(0, word3)
                                    words_exist.append(word3)
                                    weights.insert(0, word3_tfidf)
                                if (weights[i] > word3_tfidf) and (weights[i + 1] < word3_tfidf) and \
                                        (word3 not in words_exist) and (word3 not in words[0:3]):
                                    words.insert(i + 1, word3)
                                    words_exist.append(word3)
                                    weights.insert(i + 1, word3_tfidf)
                                i += 1
                            print "NewWords:",
                            for word in words:
                                print word,
                            print ''
                            print "NewWeights:",
                            print weights
        for word in words:
            if word.isdigit() or (len(word)>21 and re.match(u"[\u4e00-\u9fa5]", word)) or word.encode('utf-8').isdigit():
                words.remove(word)
        for word in words:
            for word_contain in words:
                try:
                    if (word_contain!=word) and re.search(word_contain,word)!=None and (len(word)>2):
                        words.remove(word_contain)
                except:
                    print word_contain,
        for word in words[0:3]:
            s2 = s2 + word + "/"
        s2 = s2[:-1]
        print s2
        s.append(s2)
        writer.writerow(s)
f.close()
csvfile.close()
end = time.clock()
print '\n'
print "read: %f s" % (end - start)