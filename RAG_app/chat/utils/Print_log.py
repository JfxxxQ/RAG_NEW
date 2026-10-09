# 打印混合检索、重排序的结果

def print_log(title, docs):
    print(f"{title}：")
    for index, doc in enumerate(docs, start=1):
        print(f"第{index}个文档: {doc}")