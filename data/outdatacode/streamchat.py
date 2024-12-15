# !/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, request
import threading
from flask_cors import CORS
from flask import Response
import os
from sentence_transformers import SentenceTransformer
import torch
import requests




# 获取可用的 CUDA 设备数量
device_count = torch.cuda.device_count()
print(f"可用的 CUDA 设备数量: {device_count}")


os.environ["CUDA_VISIBLE_DEVICES"] = '0,1,2,3,4'
# 这个环境变量是为了解决CUDA内存不足的问题
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

app = Flask(__name__)
CORS(app)



# 加载embeding模型  
embedding = SentenceTransformer('/data/dataEmbedding/bge-large-zh')
# 使用cuda给embedding模型加速
device = torch.device("cuda")
embedding = embedding.to(device)



# 创建线程锁和计数器
lock = threading.Lock()
counter = 0
MAX_CONCURRENT_REQUESTS = 5  # 最大并发请求数


# 在原来代码基础上添加新的路由和视图函数
@app.route('/test', methods=['GET'])
def test():#
    return 'successful'



# 流式响应生成器：将流式响应处理逻辑封装到一个生成器函数中。
def stream_response(url, headers, data):
    response = requests.post(url, headers=headers, json=data, stream=True)
    response.raise_for_status()  # 检查请求是否成功

    for chunk in response.iter_content(chunk_size=512):
        if chunk:
            decoded_chunk = chunk.decode('utf-8')
            print(decoded_chunk, end='')  # 实时打印到控制台
            yield decoded_chunk  # 逐个返回响应数据


# 多轮对话
@app.route('/baichuan/chat', methods=['POST', 'OPTIONS'])
def chat():
    global counter
    # 打印请求信息
    print(f"Request Method: {request.method}")
    print(f"Request Headers: {request.headers}")
    print(f"Request Body: {request.get_json()}")

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

    # ============开始调用大模型================
    # Step 1: 发起HTTP请求
    url = "http://localhost:8848/v1/chat/completions"  # 替换为实际的URL
    headers = {
        "Content-Type": "application/json",
       # "Authorization": "Bearer YOUR_ACCESS_TOKEN"  # 如果需要认证
    }
    data={
        "model": "ds",
        "messages": [
            {"role": "user", "content":question}
        ],
        "stream":"true"
    }

    # 使用自定义流式响应生成器
    return Response(stream_response(url, headers, data), content_type="text/event-stream")



if __name__ == '__main__':
    print("Flask 服务器已启动")
    app.run(host='0.0.0.0', port=8090)

