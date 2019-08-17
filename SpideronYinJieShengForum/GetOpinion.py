import pickle
import requests
import json


'''鉴权认证机制'''
def get_access_token():
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=【官网获取的AK】&client_secret=【官网获取的SK】'
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    response = requests.get(host, headers=headers)
    content = json.loads(response.text)
    if content:
        return content["access_token"]


'''接口接入，返回json格式数据'''
def get_content(text):
    access_token = get_access_token().strip()
    url = "https://aip.baidubce.com/rpc/2.0/nlp/v2/comment_tag?charset=UTF-8&access_token=" + access_token  # API
    headers = {"Content-Type": "application/json"}
    data = {"text": text, "type": 7}  # type包含13个类别，其中7代表教育，其他行业参考技术文档
    data = json.dumps(data, ensure_ascii=False).encode("utf-8")
    r = requests.post(url, data=data, headers=headers)
    return r.text


if __name__ == '__main__':
    f = open("应届生论坛_观点.csv", "w")
    f.write("标题,作者时间,最后发表时间,回复\n")
    with open('yingjiesheng_all.pk', 'rb') as ff:
        for e in pickle.load(ff):
            for i, p in enumerate(e["post"]):
                if i == 0:
                    f.write(e["title"].strip().replace("\r", " ").replace("\n", " ") + "," +
                            e["created_time"] + "," + e["last_time_reply"] + ",版主: " +
                            e["post"][i].strip().replace("\r", " ").replace("\n", " ") + "\n")
                else:
                    f.write(",,," + str(i) + "楼: " + e["post"][i].strip().replace("\r", " ").replace("\n", " ") + "\n")
            text = ""
            text += (e["title"].strip().replace("\r", " ").replace("\n", " ") + " ")
            text += " ".join([p.strip().replace("\r", " ").replace("\n", " ") for p in e["post"]])
            contents = get_content(text)
            contents = json.loads(contents)  # str转成dict
            if "items" in contents:
                for j, content in enumerate(contents['items']):
                    f.write(",,,观点" + str(j + 1) + ": " +
                            content["abstract"].replace("<span>", "").replace("</span>", "") + "\n")
    f.close()
