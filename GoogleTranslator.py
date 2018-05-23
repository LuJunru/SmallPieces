from GoogleFreeTrans import Translator
import pandas as pd
import numpy as np

translator = Translator.translator(src='en', dest='zh-CN')
train_df = pd.read_csv('./data/quora_train.csv')
en_question_pairs = train_df[['question1', 'question2', 'is_duplicate']]
question_pairs = np.insert(np.insert(en_question_pairs.get_values(), 2, values=np.zeros(len(en_question_pairs)), axis=1)
                           , 2, values=np.zeros(len(en_question_pairs)), axis=1)
start_point = 100000
save_interval = 1000
print_interval = 100
for i in range(start_point, len(question_pairs)):
    try:
        question_pairs[i][2] = translator.translate(question_pairs[i][0])
        question_pairs[i][3] = translator.translate(question_pairs[i][1])
    except:
        print(i)  # 把可能因为网络连接中断、字符错误等没有翻译成功的行都打印出来，以便后续手动操作
    if i % print_interval == 0 and i != 0:
        print(str(i) + " sentences translated")
    if i % save_interval == 0 and i != start_point:
        save = pd.DataFrame(question_pairs[i - save_interval:i])
        save.to_csv('data/cn_quora_train' + str(i - save_interval + 1) + '-' + str(i) + '.csv', index=False, sep=',',
                    header=['question1', 'question2', 'cn_question1', 'cn_question2', 'is_duplicate'], encoding='utf-8')