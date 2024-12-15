from pymilvus import connections, Collection, AnnSearchRequest

# 连接到Milvus
connections.connect(
    host="10.14.2.38", # 用你的Milvus服务器IP替换
    port="19530"
)
 
# 搜索

queryStr = "一位面容消瘦的中年男子，留着一缕胡须，身穿道袍，手拿鹅毛扇，站在高处，若有所思地眺望着远方"

from sentence_transformers import SentenceTransformer
model = SentenceTransformer('/home/baichuan2-7b/dataEmbedding/bge-large-zh')

import torch
device = torch.device("cuda")
model = model.to(device)
# 为filmVector创建ANN搜索请求1
query_vector = model.encode([queryStr])[0].tolist()

query_filmVector = {
    "vector": query_vector
}
 
search_param_1 = {
    "data": query_filmVector,  # 查询向量
    "anns_field": "vector",  # 向量字段名
    "param": {
        "metric_type": "L2",  # 此参数值必须与集合模式中使用的参数值相同
        "params": {"nprobe": 10}
    },
    "limit": 2  # 此AnnSearchRequest返回的搜索结果数量
}
request_1 = AnnSearchRequest(**search_param_1)

# 为posterVector创建ANN搜索请求2
query_posterVector = [[0.02550758562349764, 0.006085637357292062, 0.5325251250159071, 0.7676432650114147, 0.5521074424751443]]
search_param_2 = {
    "data": query_posterVector,  # 查询向量
    "anns_field": "XXXXXXXX",  # 向量字段名
    "param": {
        "metric_type": "L2",  # 此参数值必须与集合模式中使用的参数值相同
        "params": {"nprobe": 10}
    },
    "limit": 2  # 此AnnSearchRequest返回的搜索结果数量
}
request_2 = AnnSearchRequest(**search_param_2)
 
# 将这两个请求作为一个列表存储在`reqs`中
reqs = [request_1, request_2]


from pymilvus import WeightedRanker
# 使用WeightedRanker结合指定的权重来组合结果
# 将0.8的权重分配给文本搜索，将0.2的权重分配给图像搜索
rerank = WeightedRanker(0.8, 0.2)  


# 或者，使用RRFRanker进行倒数排名融合重新排序
from pymilvus import RRFRanker
 
rerank = RRFRanker()


# 获取名为 'demod' 的集合
collection = Collection("demo")

# 加载集合到内存
collection.load()
 
res = collection.hybrid_search(
    reqs, # 在步骤1中创建的AnnSearchRequest对象的列表
    rerank, # 在步骤2中指定的重排序策略
    limit=2 # 返回的最终搜索结果数量
)
 
print(res)