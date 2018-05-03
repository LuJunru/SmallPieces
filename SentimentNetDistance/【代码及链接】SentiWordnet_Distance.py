# -*- coding: utf-8 -*-
# @Author  : junru.lu@enactusuir.org
# @File    : run.py
# @Software: PyCharm
# @Environment : Python 3.6+

# 基础包
import os
import pickle

# 编码相关包
import importlib, sys
importlib.reload(sys)

'''
本文件用于调用SentimentNet，及以此为基础进行词间语义距离的计算; 没有实现路径存储，有兴趣可以试一下

资源下载：https://github.com/sanju1920/Sentiment-Analysis-Using-Sentiwordnet-in-Python
举个例子：estimable(1, 2, 3)----根据论文介绍目的(情感分析和意图挖掘)、架构、论文内容等
pos   syn_set  p_score  n_score  words   explanation
a 00904163    1	0	estimable#1	deserving of respect or high regard
a 01983162	1	0	respectable#2 honorable#4 good#4 estimable#2	deserving of esteem and respect; "all respectable...
a 00301432	0	0	estimable#3 computable#1	may be computed or estimated; "a calculable risk"; "computable odds"...
其中，不同字段用tab键连接，words内部用空格键连接

距离计算实现方法:1.广度优先遍历（也可以用狄杰斯特拉算法和弗洛伊德算法，以空间换时间，先把图建好）
               2.在WordNet上，方法类似，但是也有人做过高效的办法：https://github.com/soldni/WNDist

ps：句子情感评估体系：Sentiment Analysis: How to Derive Prior Polarities from SentiWordNet。
    实现算法：https://github.com/anelachan/sentimentanalysis
'''

# ------------------预加载------------------ #

cur_dir = os.path.dirname(os.path.abspath(__file__)) or os.getcwd()  # 当前项目路径，便于项目迁移时仍能继续使用


# -----------------基础函数------------------ #

def search_word(file_path, input_word):
    f = open(file_path)
    inner_flag = 0
    result_lists = []
    for line in f:
        if not line.startswith("#"):  # 避开表头
            cols = line.split("\t")
            words = [w.split("#")[0] for w in cols[4].split(" ")]  # 列表生成式

            if input_word in words:
                inner_flag = 1
                tag = cols[0]  # 词性
                inner_id = cols[1]  # 义元ID
                inner_words = "/".join([w.split("#")[0] for w in cols[4].split(" ") if input_word not in w])  # 同义词
                p_score = float(cols[2])  # 积极情感得分
                n_score = float(cols[3])  # 消极情感得分
                o_score = 1.0 - (p_score + n_score)  # 非情感得分
                content = cols[5].strip()
                result_lists.append((tag, inner_id, inner_words, p_score, n_score, o_score, content))

    return inner_flag, result_lists


def build_structured_dictionary(file_path):
    f = open(file_path)
    structured_dict = {}
    for line in f:
        if not line.startswith('#'):
            cols = line.split("\t")
            words = [w.split("#")[0] for w in cols[4].split(" ")]
            inner_id = cols[1]  # 义元ID
            for inner_word in words:
                inner_words = [w.split("#")[0] for w in cols[4].split(" ") if inner_word not in w]  # 同义词
                if len(inner_words) > 0:
                    if inner_word in structured_dict:  # 如果字典中已经有这个key
                        structured_dict[inner_word][inner_id] = inner_words
                    else:
                        structured_dict[inner_word] = {inner_id: inner_words}

    return structured_dict

# ------------------主函数------------------ #

if __name__ == "__main__":

    # 86-110行描述从词典中查询一个词及其全部相关义元
    word = input("请输入要查询的词: ")
    print("="*5 + "结果如下" + "="*5)
    records = search_word(cur_dir + "/SentiWordNet_3.0.0_20130122.txt", word)
    flag = records[0]
    records_lists = records[1]
    if flag == 0:
        print("查无此词！")
    else:
        for record in records_lists:
            syn_id = record[1]
            pos_tag = record[0]
            syn_words = record[2]
            positive_score = record[3]
            negative_score = record[4]
            objective_score = record[5]
            explanation = record[6]

            print("义元编号：" + syn_id)
            print("词性：" + pos_tag)
            print("同义词：" + syn_words)
            print("积极：" + str(positive_score))
            print("消极：" + str(negative_score))
            print("非情感：" + str(objective_score))
            print("释义：" + explanation)
            print("-" * 20)

    # 113-124行描述为词典中的词建成我们想要的字典，并做简要查看
    # 字典内键值对形如：{estimable: {01983162: [respectable, honorable, good], 00301432: [computable]}}
    sentiment_dict = build_structured_dictionary(cur_dir + "/SentiWordNet_3.0.0_20130122.txt")
    '''
    # 如果字典太大不想每次都存储，可以使用pickle包
    pickle.dump(sentiment_dict, open(cur_dir + '/structured_sentiment_dict_version3.0.0_20180420.pkl', 'wb'))
    sentiment_dict = pickle.load(open(cur_dir + '/structured_sentiment_dict_version3.0.0_20180420.pkl', 'rb'))
    '''
    print(len(sentiment_dict))
    for key in sentiment_dict:
        if key == word:
            print(key, sentiment_dict[key])
    print('='*20)

    # 127-153行描述使用建好的字典进行距离计算
    target_word = input("请输入终点词: ")
    target_records = search_word(cur_dir + "/SentiWordNet_3.0.0_20130122.txt", target_word)
    target_flag = target_records[0]
    if target_flag == 0:  # 没有这个词直接无法到达即可
        print("无法到达")
    else:
        word_set = [word]  # 上一轮结束查询时，已经查到的全部词
        read_set = set()  # 已经读到过的词
        distance = 0
        while target_word not in word_set:  # 这种方法比较适用距离不超过10的单词对，然而这个词表内部的词的距离一般不超过10
            distance += 1
            word_subset = []
            for current_word in word_set:  # 遍历已经查到的全部词
                if current_word in sentiment_dict and current_word not in read_set:  # 确保字典中有这个词，并且还没有被查过
                    current_word_subset = sum([sentiment_dict[current_word][current_word_id] for current_word_id in
                                               sentiment_dict[current_word]], [])  # 当前词的全部同义词
                    word_subset += current_word_subset  # 合并当前词的同义词
                    read_set.add(current_word)
            # 当前轮查到的全部新词
            new_set = [new_word for new_word in set(word_subset) if
                       new_word not in read_set and new_word not in word_set]
            word_set += new_set
            if len(new_set) == 0:
                distance = "无法到达"
                break
            print(word, target_word, new_set)
        print(distance)