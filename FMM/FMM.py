#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : ***
# @Author  : Lu Junru
# @Site    : 
# @File    : FMM.py
# @Software: PyCharm

import re
import codecs

# load dictionary
def load_dic():
    f1 = codecs.open('wordlist.txt','r','gbk')
    dic = f1.read()
    f1.close()
    # 使用正则表达式去除数字及空格
    p = re.compile(r'\d+')
    dic = re.sub(p,'',dic)
    dic = re.sub(' ','',dic)
    dic = dic.splitlines()
return dic

# load unsegment.txt
def load_unseg():
    f2 = codecs.open('unsegment2.txt','r','utf-8')
    unseg = f2.read()
    f2.close()
    # 使用正则表达式去除标点符号
    punctuation = re.compile(ur'[，。《》\\n]')
    unseg = re.split(punctuation, unseg)
    return unseg

# FMM
def FMM(sents, MaxLen):
    s1 = sents;
    s2 = '';

    while s1 != '':
        lens = MaxLen
        if len(s1) < lens:
            lens = len(s1)
        word = s1[:lens]
        dic = load_dic()
        while word not in dic and len(word)!=1:
            word = word[:len(word)-1]       
        s2 = s2 + word + '\\'
        s1 = s1[len(word):]
    return s2

unsegs = load_unseg()
for unseg in unsegs:
    print unseg
    print FMM(unseg,4)
