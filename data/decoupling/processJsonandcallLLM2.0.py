# !/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, request, jsonify
import threading
from flask_cors import CORS
from flask import Response
import os
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient, DataType
import json
import torch
from tempfile import NamedTemporaryFile
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from requests_toolbelt.streaming_iterator import StreamingIterator
import yaml

# 读取配置文件
def read_yaml_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# 读取配置文件
config = read_yaml_config('./application.yaml')

# 访问配置项
server_port = config['server']['port']
milvus_host = config['milvus']['host']
milvus_port = config['milvus']['port']
llm_name = config['llm']['name']
llm_host = config['llm']['host']
llm_port = config['llm']['port']
cuda_device = config['cuda']['device']
bge_dir = config['modules']['embedding']['bge']

print(f"server_port: {server_port}")
print(f"milvus_host: {milvus_host}")
print(f"milvus_port: {milvus_port}")
print(f"llm_name: {llm_name}")
print(f"llm_host: {llm_host}")
print(f"llm_port: {llm_port}")
print(f"cuda_device: {cuda_device}")
print(f"bge_dir: {bge_dir}")



# 设置一个Milvus客户端
milvus_uri = f"http://{milvus_host}:{milvus_port}"
print(f"milvus_uri: {milvus_uri}")
client = MilvusClient(
    uri=milvus_uri,
)

# 获取可用的 CUDA 设备数量
device_count = torch.cuda.device_count()
print(f"可用的 CUDA 设备数量: {device_count}")


os.environ["CUDA_VISIBLE_DEVICES"] = str(cuda_device)
# 这个环境变量是为了解决CUDA内存不足的问题
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

app = Flask(__name__)
CORS(app)



# 加载embeding模型  
embedding = SentenceTransformer(bge_dir)
# 使用cuda给embedding模型加速
device = torch.device("cuda")
embedding = embedding.to(device)



# 创建线程锁和计数器
lock = threading.Lock()
counter = 0
MAX_CONCURRENT_REQUESTS = 5  # 最大并发请求数


llm_uri = f"http://{llm_host}:{llm_port}"
print(f"llm_uri: {llm_uri}")

@app.route('/baichuan/cntreview', methods=['POST', 'OPTIONS'])
def conversation():
    global counter
    print("receive request!")
    if request.method == 'OPTIONS':
        # 处理预检请求
        response = app.make_default_options_response()
        headers = response.headers

        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
        return response, 200  # 返回200 OK状态
    # 请求过载，返回提示信息
    if counter >= MAX_CONCURRENT_REQUESTS:
        return jsonify({'message': '请稍等再试'})
    print("option end")
    # 获取线程锁
    with lock:
        counter += 1

    try:
        # Step 1: 从请求中提取 PDF 文件
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        print("have got pdf")

        # 从请求中提取流和数据库名称，默认使用流式处理和 demo 数据库
        isStream = request.form.get("stream")
        db = request.form.get("db")
        if not isStream:
            isStream = True
            print("没携带stream参数，默认使用流式处理")
        # isStream 从请求获取的是字符串，需要转换为布尔值！！在if判断时一直是True
        else:
            isStream=False  
        
        if not db:
            db = "demo"
            print("没携带db参数，默认使用 demo 数据库")
        else:
            print("携带了db参数，使用的数据库是：", db)

        # Step 2: 将 PDF 文件内容写入临时文件
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(file.read())
            temp_pdf_path = temp_pdf.name
        
        # Step 3: 使用 PyPDFLoader 加载临时文件
        try:
            loader = PyPDFLoader(temp_pdf_path)
            documents = loader.load()
            
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
            chunks = text_splitter.split_documents(documents)
            
            # 打印所有文本块    
            for chunk in chunks:
                print(chunk.page_content)
                print("=================================================")
            
            template="["

            # 根据文本块在 Milvus 中搜索并拼接
            # 为filmVector创建ANN搜索请求1
            for chunk in chunks:
                query_vector = embedding.encode([chunk.page_content])[0].tolist()
                # 加载集合到内存，这样才能搜索，否则就要在Attu或命令行中手动装载！
                client.load_collection(db)#是幂等的，所以不用担心重复加载
                # 单向量搜索
                res = client.search(
                    collection_name=db, # 用你的集合的实际名称替换
                    data=[query_vector], # 用你的查询向量替换！！这样才是对的
                    limit=2, # 返回的搜索结果的最大数量
                    search_params={"metric_type": "L2", "params": {}}, # 搜索参数，这里的L2表示欧几里得距离，创建集合时使用的是L2这里也要使用L2
                    output_fields=[ "text"]  # 指定返回的字段   
                )
                # data: List[List[float]],  # 查询向量，通常是一个二维列表
                # 将输出转换为格式化的JSON字符串    
                result = json.dumps(res, indent=4, ensure_ascii=False)
                
                # 解析JSON字符串为Python对象
                result = json.loads(result)
                
                #result是 [[{}……]]
                texts = result[0][0]['entity']['text']+" "+result[0][1]['entity']['text']
                

                template+="{\"record\":\""+texts+"\",\"content\":\""+chunk.page_content+"\",\"advice\":\"______\"},\"level\":\"\"},"


            #template=""
            # 去掉最后一个逗号
            template = template[:-1]
            template+="]"
            # 解析JSON字符串为Python对象
            #template = json.loads(template) 
            # 格式化template成为JSON字符串
            template = json.dumps(template, indent=4, ensure_ascii=False)
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        question=template+"  这是一篇合同的数据，“content”是分片后得到的合同内容，结合“record”(劳动法的内容片段)推断“advice”和“level”；注意：最后返回的是一个JSON数组而且元素数量和上面的数据严格一致，每个JSON需要包含“content”、“advice”和“level”这3个字段以及对应的值其中“content”字段的值可以从直接返回。“advice”根据“record”结合“content”提出你的建议，“level”的值根据潜在的风险评估填写高、中、低3个值。不用返回“record”->"
        #print(question)
        #这是一篇合同数据，“审核”是分片后的合同内容，根据“案卷”填写“审核结果”和“风险等级”；注意：最后返回的是一个JSON数组，每个元素是一个JSON对象，需要包含上文json“审核”、“审核结果”和“风险等级(高、中、低)”3个字段以及对应的值。
        
         # ============开始调用大模型================
        # Step 1: 发起HTTP请求
        url = f"{llm_uri}/v1/chat/completions"  # 替换为实际的URL
        print(url)
        headers = {
            "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # 如果需要认证
        }
        data={
            "model": llm_name,
            "messages": [
                {"role": "user", "content":question}
            ],
            "stream":isStream
        }

        if isStream:
            print("使用流式处理")
            # 使用自定义流式响应生成器
            return Response(stream_response(url, headers, data), content_type="text/event-stream")
        else:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # 检查请求是否成功
            return response.json()
        

    finally:
        # 释放线程锁并减少计数器
        with lock:
            counter -= 1
# 在原来代码基础上添加新的路由和视图函数
@app.route('/test', methods=['GET'])
def test():#
    return 'successful'



# 流式响应生成器：将流式响应处理逻辑封装到一个生成器函数中。
def stream_response(url, headers, data):
    response = requests.post(url, headers=headers, json=data, stream=True)
    response.raise_for_status()  # 检查请求是否成功

    for chunk in response.iter_content(chunk_size=500):
        if chunk:
            decoded_chunk = chunk.decode('utf-8')
            print(decoded_chunk, end='')  # 实时打印到控制台
            yield decoded_chunk  # 逐个返回响应数据


# 多轮对话
@app.route('/baichuan/chat', methods=['POST', 'OPTIONS'])
def chat():
    global counter
    if request.method == 'OPTIONS':
        # 处理预检请求
        response = app.make_default_options_response()
        headers = response.headers

        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
        return response, 200  # 返回200 OK状态
    # 取出请求中的question的json数据
    question = request.json.get("question")
    message=[]
    message.append({"role": "user", "content": question})

    # ===============开始调用大模型================
    # Step 1: 发起HTTP请求
    url = f"{llm_uri}/v1/chat/completions"  # 替换为实际的URL
    headers = {
        "Content-Type": "application/json",
       # "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # 如果需要认证
    }
    data={
        "model": llm_name,
        "messages": [
            {"role": "user", "content":question}
        ],
        "stream":"true"
    }

    # 使用自定义流式响应生成器
    return Response(stream_response(url, headers, data), content_type="text/event-stream")


# 写一个函数，获取milvus里所有collection的名称
@app.route('/get/collections', methods=['GET'])
def get_collections():
    # 获取所有的集合名称
    collections = client.list_collections()
    print(type(collections))
    return jsonify(collections)

# 删除集合
@app.route('/delete/collection', methods=['DELETE'])
def deletecollection():
    # 从URL获取参数
    collection_name = request.args.get('collectioname')
   # 删除集合
    if collection_name:
        client.drop_collection(collection_name)
        return jsonify({"message": "This is type 1 request"})
    else:
        return jsonify({"message": "请提供集合名称"})

# 往collection里插入数据
@app.route('/embed/pdf', methods=['POST', 'OPTIONS'])
def embedpdf():
    if request.method == 'OPTIONS':
        # 处理预检请求
        response = app.make_default_options_response()
        headers = response.headers

        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
        return response, 200  # 返回200 OK状态


    # Step 1: 从请求中提取 PDF 文件
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Step 2: 将 PDF 文件内容写入临时文件
    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(file.read())
        temp_pdf_path = temp_pdf.name
    
    # Step 3: 使用 PyPDFLoader 加载临时文件
    
    loader = PyPDFLoader(temp_pdf_path)
    documents = loader.load()
    

    size = request.form.get('size')
    overlap = request.form.get('overlap')
    mycollection_name = request.form.get('collection_name')

    # TODO：从请求的 form-data 中提取的是字符串，需要转换为整数
    size = int(size) if size else 400
    overlap = int(overlap) if overlap else 50

    print("size:", size)
    print("overlap:", overlap)
    print("collection_name:", mycollection_name)



    text_splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    chunks = text_splitter.split_documents(documents)
    
    # 打印所有文本块，并将文本块插入到milvus中    
    for chunk in chunks:
        print(chunk.page_content)
        print("=================================================")
        #print(chunk)测试过，chunk和chunk.page_content都是字符串
        mydata={
            "vector":embedding.encode([chunk.page_content])[0].tolist(),
            "text":chunk.page_content
        }
        # 3. 插入实体到集合中
        res=client.insert(
            collection_name=mycollection_name,
            data=mydata
        )
        print("res:",res)

    return jsonify({"message": "This is type 1 request"})


# 创建集合
@app.route('/create/collection', methods=['PUT'])
def createcollection():
     # 获取请求体中的参数
    data = request.get_json()
    name = data.get('name', 'demo')  # 默认集合名称为 'demo'
    mydim=data.get('dim',1024)
    mymax_length=data.get('max_length',4096)
    nlist=data.get('nlist',3)
    print("收到数据===>name:%s,dim:%s,max_length:%s,nlist%s"%(name,mydim,mymax_length,nlist))


    schema = MilvusClient.create_schema(
    auto_id=True,
    enable_dynamic_field=False,
    )
    # 创建模式

    schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True),
    schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=mydim), 
    schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=mymax_length)
   
    # 为字段创建索引
    index_params = client.prepare_index_params()
    index_params.add_index(
    field_name="vector",
    metric_type="L2",
    index_type= "IVF_FLAT",
    params= {"nlist": nlist}
    )
    
    client.create_collection(
    collection_name=name,
    schema=schema,
    index_params=index_params
    )

    return jsonify({"message": "集合创建成功！"})

    

if __name__ == '__main__':
    print("Flask 服务器已启动")
    app.run(host='0.0.0.0', port=server_port)

