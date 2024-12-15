from flask import Blueprint, jsonify,request
from tempfile import NamedTemporaryFile
from langchain.document_loaders import PyPDFLoader
# 加载预训练模型
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymilvus import connections, Collection, MilvusClient,FieldSchema, CollectionSchema, DataType
from .MilvusLink import MilvusLink as Milvus
import json
import torch

model = SentenceTransformer('/data/dataEmbedding/bge-large-zh')

device = torch.device("cuda")
model = model.to(device)
dochandler = Blueprint('dochandler', __name__)


@dochandler.route('/embed/pdf', methods=['POST', 'OPTIONS'])
def embedpdf():
    if request.method == 'OPTIONS':
        # 处理预检请求
        response = dochandler.make_default_options_response()
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
    
    # 从请求的 form-data 中提取名为 json 的字符串
    if 'json' not in request.form:
        return jsonify({"error": "No JSON data part in the request"}), 400
    
    try:
        data = json.loads(request.form['json'])
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON data"}), 400
    

    size = data.get('size', 400)
    overlap = data.get('overlap', 50)
    mycollection_name = data.get('name', 'XXXX')

    print("collection_name:", mycollection_name)


    text_splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
    chunks = text_splitter.split_documents(documents)
    
    # 打印所有文本块，并将文本块插入到milvus中    
    for chunk in chunks:
        print(chunk.page_content)
        print("=================================================")
        #print(chunk)测试过，chunk和chunk.page_content都是字符串
        mydata={
            "vector":model.encode([chunk.page_content])[0].tolist(),
            "text":chunk.page_content
        }
        # 3. 插入实体到集合中
        res=Milvus.client.insert(
            collection_name=mycollection_name,
            data=mydata
        )
        print("res:",res)

    return jsonify({"message": "This is type 1 request"})

    
    