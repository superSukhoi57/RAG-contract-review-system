# !/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, request, jsonify
import threading
from flask_cors import CORS
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from sentence_transformers import SentenceTransformer
from pymilvus import MilvusClient
import json
import torch
from transformers import BitsAndBytesConfig


# 设置一个Milvus客户端
client = MilvusClient(
    uri="http://10.14.2.38:19530"
)

# 获取可用的 CUDA 设备数量
device_count = torch.cuda.device_count()
print(f"可用的 CUDA 设备数量: {device_count}")


os.environ["CUDA_VISIBLE_DEVICES"] = '0,1,2,3,4, 5'
# 这个环境变量是为了解决CUDA内存不足的问题
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

app = Flask(__name__)
CORS(app)

# 解决The `load_in_4bit` and `load_in_8bit` arguments are deprecated and will be removed in the future versions. Please, pass a `BitsAndBytesConfig` object in `quantization_config` argument instead.
# 创建 BitsAndBytesConfig 对象
quantization_config = BitsAndBytesConfig(load_in_8bit=True)  # 或者 load_in_4bit=True


# 加载LLM,最后一个是解决CUDA内存不足的问题
tokenizer = AutoTokenizer.from_pretrained("/data/baichuan2-7b/Baichuan2-7B-Chat", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("/data/baichuan2-7b/Baichuan2-7B-Chat", device_map="auto", trust_remote_code=True,quantization_config=quantization_config)
# 加载LLM
#tokenizer = AutoTokenizer.from_pretrained("/data/baichuan2-7b/Baichuan2-7B-Chat", trust_remote_code=True)
#model = AutoModelForCausalLM.from_pretrained("/data/baichuan2-7b/Baichuan2-7B-Chat", device_map="auto", trust_remote_code=True,load_in_8bit = True)
# 加载embeding模型
embedding = SentenceTransformer('/data/baichuan2-7b/dataEmbedding/bge-large-zh')
# 使用cuda给embedding模型加速
device = torch.device("cuda")
embedding = embedding.to(device)



# 创建线程锁和计数器
lock = threading.Lock()
counter = 0
MAX_CONCURRENT_REQUESTS = 5  # 最大并发请求数


@app.route('/baichuan/conversation', methods=['POST'])
def conversation():
    global counter

    # 请求过载，返回提示信息
    if counter >= MAX_CONCURRENT_REQUESTS:
        return jsonify({'message': '请稍等再试'})

    # 获取线程锁
    with lock:
        counter += 1

    try:
        # 接收 POST 请求的数据，获取问题
        question = request.json['question']
        question += '->'
        # 将问题转换为向量使用bge-large-zh的embedding模型
        query_vector = embedding.encode([question])[0].tolist()
        # 将问题进行单向量搜索
        res = client.search(
            collection_name="demo", # 用你的集合的实际名称替换
            data=[query_vector], # 用你的查询向量替换！！这样才是对的
            limit=3, # 返回的搜索结果的最大数量
            search_params={"metric_type": "L2", "params": {}}, # 搜索参数，这里的L2表示欧几里得距离，创建集合时使用的是L2这里也要使用L2
            output_fields=[ "text"]  # 指定返回的字段   
        )

        #将搜索转换为格式化的JSON字符串    
        result = json.dumps(res, indent=4, ensure_ascii=False)#没有ensure_ascii=False的话，中文会被转换为Unicode编码
        #print(result)
        # 拼接问题和搜索结果
        question = result+" \n 要求：1，先简要概括上面的提示内容;2、再根据上面的提示内容，回答问题："+question
        print(question)
        print("+=========================================================================================+")
        inputs = tokenizer(question, return_tensors='pt')
        # 清理未分配的缓存内存
        torch.cuda.empty_cache()
        inputs = inputs.to('cuda:0')
        pred = model.generate(**inputs, max_new_tokens=1024, repetition_penalty=1.1)

        text = tokenizer.decode(pred.cpu()[0], skip_special_tokens=True)
        print("result:", text)
        
        # 返回结果
        response = {'result': text[len(question):]}
        
        return jsonify(response)

    finally:
        # 释放线程锁并减少计数器
        with lock:
            counter -= 1
# 在原来代码基础上添加新的路由和视图函数
@app.route('/test', methods=['GET'])
def test():
    return 'successful'


if __name__ == '__main__':
    print("Flask 服务器已启动")
    app.run(host='0.0.0.0', port=8899)
