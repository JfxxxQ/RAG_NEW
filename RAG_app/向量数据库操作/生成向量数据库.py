import pandas as pd
import os
from pathlib import Path
from langchain_core.documents import Document
from RAG_app.common.LoadChromaConn import LoadChromaConn
from langchain_chroma import Chroma

file_path = os.path.join(Path(os.path.dirname(__file__)), "../datasets", "新闻.csv")

result = pd.read_csv(filepath_or_buffer=file_path, encoding="gbk")
# print(result)
# print(type(result))
"""
       source        type                                               text
0         新华社    censored  新华社昆明６月２０日体育专电（记者侯文坤 王晋源）２０１４年洲际国奥男篮争霸赛７月５日至７日...
1         人民网    censored  人民网北京5月27日电 为深入贯彻落实党的群众路线实践教育活动，进一步密切联系少数民族群众，...
2         新华社    censored  新华社内罗毕6月18日体育专电 在尼日利亚北部城市达马图鲁的一个观看世界杯比赛的地点17日晚...
3         人民网    censored   6月20日，河南省安阳市内黄县农民在当地一家粮食收购点喜售丰收粮。今年河南省夏粮再获丰收，...
4         人民网    censored   土伦杯-连续被判两点球&nbsp;国奥1-4负葡萄牙无缘四强 人民网5月28日电 北京时间...
"""
result_list = result['text'].to_list()
# print(result_list)
data_list = []
for item in result_list:
    data_list.append(
        Document(page_content=item, metadata={"source": file_path})
    )
# print(len(data_list[0].page_content))
# # 或者打印第一条数据的完整内容，不做省略
# pd.set_option('display.max_colwidth', None)
# print(result['text'][0])
chroma_data_path = os.path.join(Path(os.path.dirname(__file__)).parent, "chroma_data", "new_data")
collection_name = "new"
embedding_model = LoadChromaConn().embedding_model
try:
    Chroma.from_documents(
        documents=data_list,
        embedding=embedding_model,
        persist_directory=chroma_data_path,
        collection_name=collection_name
    )
    print("创建成功")
except Exception as e:
    print(e)
    print("创建失败")