
# 加载预训练模型
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient

# 设置一个Milvus客户端
client = MilvusClient(
    uri="http://10.14.1.2:19530"
)
model = SentenceTransformer('/data/dataEmbedding/bge-large-zh',device='cuda')



print("Max Sequence Length:", model.max_seq_length)
# Change the length to 200
model.max_seq_length = 200
print("After Change Max Sequence Length:", model.max_seq_length)
# 不能将长度增加到高于相应 transformer 模型的最大支持长度

message="你好！"

example=model.encode(message)# 是一个列表
print("type of model.encode() %s ; model.encode=%r",type(example),example)
print("demension of model.encode() %s",len(example))


mydata={
    "bgevector":model.encode(message),
    "msg":1
}
# 3. 插入实体到集合中
res=client.insert(
    collection_name="bgetest",
    data=mydata
)
print("res:",res)




message="嘿！你好啊！"

# 单向量搜索
mysearch = client.search(
    collection_name="bgetest", # 用你的集合的实际名称替换
    data=[model.encode(message)], # 用你的查询向量替换！！这样才是对的
    limit=2, # 返回的搜索结果的最大数量
    search_params={"metric_type": "L2", "params": {}}, # 搜索参数，这里的L2表示欧几里得距离，创建集合时使用的是L2这里也要使用L2
    output_fields=[ "msg"]  # 指定返回的字段   
)

print("mysearch:",mysearch)