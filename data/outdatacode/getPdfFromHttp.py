from flask import Flask, request, jsonify
from io import BytesIO
from tempfile import NamedTemporaryFile
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from pymilvus import MilvusClient
import json
import torch
from sentence_transformers import SentenceTransformer

# 加载embeding模型
model = SentenceTransformer('/data/baichuan2-7b/dataEmbedding/bge-large-zh')
device = torch.device("cuda")
model = model.to(device)

# 1. 设置一个Milvus客户端
client = MilvusClient(
    uri="http://10.14.2.38:19530"
)


app = Flask(__name__)


@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
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
    try:
        loader = PyPDFLoader(temp_pdf_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        
        # 打印所有文本块    
        for chunk in chunks:
            print(chunk.page_content)
            print("=================================================")
        
        template="["

        # 根据文本块在 Milvus 中搜索并拼接
        # 为filmVector创建ANN搜索请求1
        for chunk in chunks:
            query_vector = model.encode([chunk.page_content])[0].tolist()
            # 加载集合到内存，这样才能搜索，否则就要在Attu或命令行中手动装载！
            #client.load_collection("demo")
            # 单向量搜索
            res = client.search(
                collection_name="demo", # 用你的集合的实际名称替换
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
            

            template+="{\"根据\":\""+texts+"\",\"审核\":\""+chunk.page_content+"\",\"审核结果\":\"______\"},\"风险等级\":\"\"},"

        # 去掉最后一个逗号
        template = template[:-1]
        template+="]"
        # 解析JSON字符串为Python对象
        #template = json.loads(template) 
        # 格式化template成为JSON字符串
        template = json.dumps(template, indent=4, ensure_ascii=False)
        print(template)
        return jsonify({"message": "PDF processed successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    print("Flask 服务器已启动")
    app.run(host='0.0.0.0', port=8899)



# TODO：经过测试 这个python代码可以正常在http拿到pdf并有逻辑地切分文本块
