

#
# TODO：这个文件是最开始写来管理collection的，后来集成了milvus的attu，所以暂时不用这个文件
#

from flask import Blueprint, jsonify,request
from pymilvus import connections, Collection, MilvusClient,FieldSchema, CollectionSchema, DataType
from .MilvusLink import MilvusLink as Milvus

collectionhandler = Blueprint('collectionhandler', __name__)

# 创建集合
@collectionhandler.route('/create/collection', methods=['PUT'])
def createcollection():
     # 获取请求体中的参数
    data = request.get_json()
    collection_name = data.get('name', 'demo')  # 默认集合名称为 'demo'


    schema = MilvusClient.create_schema(
    auto_id=True,
    enable_dynamic_field=False,
    )
    # 创建模式

    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True),
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024), 
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=4096)
   
    # 为字段创建索引
    index_params = Milvus.client.prepare_index_params()
    index_params.add_index(
    field_name="vector",
    metric_type="L2",
    index_type= "IVF_FLAT",
    params= {"nlist": 3}
    )
    
    Milvus.client.create_collection(
    collection_name=collection_name,
    schema=schema,
    index_params=index_params
    )

    return jsonify({"message": "This is type 1 request"})


# 删除集合
@collectionhandler.route('/delete/collection', methods=['DELETE'])
def deletecollection():
    # 获取请求体中的参数
    data = request.get_json()
    collection_name = data.get('name', 'demo')
   # 删除集合
    Milvus.client.drop_collection(collection_name)
    return jsonify({"message": "This is type 1 request"})



# 查找所有的集合
@collectionhandler.route('/list/collections', methods=['GET'])
def listcollections():
    # 获取所有集合
    collections = Milvus.client.list_collections()
    return jsonify({"collections": collections})


