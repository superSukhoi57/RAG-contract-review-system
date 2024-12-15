from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType


# 连接到Milvus
connections.connect(
    host="10.14.1.2", # 用你的Milvus服务器IP替换
    port="19530"
)

# 创建模式
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True,auto_id=True),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024), 
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096)
] 
 
schema = CollectionSchema(fields=fields,enable_dynamic_field=False)
 
# 创建集合
collection = Collection(name="demo", schema=schema)
 
# 为字段创建索引
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 3},
}

collection.create_index("vector", index_params)
 
# 关闭与Milvus服务器的连接
connections.disconnect(alias="default")