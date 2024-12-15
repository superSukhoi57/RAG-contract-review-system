from pymilvus import MilvusClient
import json
# 1. 设置一个Milvus客户端
client = MilvusClient(
    uri="http://10.14.1.2:19530"
)

# 搜索

queryStr = "一位面容消瘦的中年男子，留着一缕胡须，身穿道袍，手拿鹅毛扇，站在高处，若有所思地眺望着远方"

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('/data/dataEmbedding/bge-large-zh')

import torch
device = torch.device("cuda")
model = model.to(device)
# 为filmVector创建ANN搜索请求1
query_vector = model.encode([queryStr])[0].tolist()

# 加载集合到内存，这样才能搜索，否则就要在Attu或命令行中手动装载！
client.load_collection("demo")

# 单向量搜索
res = client.search(
    collection_name="demo", # 用你的集合的实际名称替换
     data=[query_vector], # 用你的查询向量替换！！这样才是对的
    limit=3, # 返回的搜索结果的最大数量
    search_params={"metric_type": "L2", "params": {}}, # 搜索参数，这里的L2表示欧几里得距离，创建集合时使用的是L2这里也要使用L2
    output_fields=[ "text"]  # 指定返回的字段   
)
# data: List[List[float]],  # 查询向量，通常是一个二维列表
 
# 将输出中的Unicode编码转换为中文
# for result in res:
#     for item in result:
#         print(item['entity']['text']) #这里输出的是中文，下面不用转
#         item['entity']['text'] = item['entity']['text'].encode().decode('unicode_escape')
#         print(item['entity']['text']) 

#将输出转换为格式化的JSON字符串    
result = json.dumps(res, indent=4, ensure_ascii=False)#没有ensure_ascii=False的话，中文会被转换为Unicode编码
print(result)

# 将集合下线
client.release_collection("demo")
