import jieba
import pickle
import matplotlib.pyplot as plt
from wordcloud import WordCloud

stop_words = set([s_w.strip() for s_w in open(【停用词路径】, "r").readlines()])


def frequency(content):
    """
    1.分词并去掉停用词
    2.词频统计
    """
    words = jieba.cut(content, cut_all=False)
    dictory = {}

    for w in words:
        w = w.lower()
        if w in stop_words or len(w) < 2:
            continue
        dictory[w] = dictory.get(w, 0) + 1

    return dictory


def wordcloud(words, shape):
    """
    绘制词云
    """
    wc = WordCloud(max_words=200,
                   width=1000,
                   height=1000,
                   mask=plt.imread(shape),
                   font_path=【中文字体路径】,
                   background_color="white",
                   margin=5)
    wc.generate_from_frequencies(words)
    plt.figure(figsize=(10, 10))
    plt.imshow(wc)
    plt.axis("off")
    plt.savefig("wordcloud.png")


allwords = ""
with open('yingjiesheng_all.pk', 'rb') as f:
    for i, e in enumerate(pickle.load(f)):
        allwords += (e["title"].strip().replace("\r", " ").replace("\n", " ") + " ")
        allwords += " ".join([p.strip().replace("\r", " ").replace("\n", " ") for p in e["post"]])
words = frequency(allwords)
wordcloud(words, 【遮罩图路径】)
