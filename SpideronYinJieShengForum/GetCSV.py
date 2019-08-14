import pickle
import pandas as pd

csv_f = {"标题": [], "作者时间": [], "最后发表时间": [], "回复": []}
with open('yingjiesheng_all.pk', 'rb') as f:
    for e in pickle.load(f):
        for i, p in enumerate(e["post"]):
            if i == 0:
                csv_f["标题"].append(e["title"])
                csv_f["作者时间"].append(e["created_time"])
                csv_f["最后发表时间"].append(e["last_time_reply"])
                csv_f["回复"].append("版主: " + p.strip().replace("\r", "").replace("\n", ""))
            else:
                csv_f["标题"].append("")
                csv_f["作者时间"].append("")
                csv_f["最后发表时间"].append("")
                csv_f["回复"].append(str(i) + "楼: " + p.strip().replace("\r", "").replace("\n", ""))
pd.DataFrame(csv_f).to_csv("应届生论坛.csv", index=False)
