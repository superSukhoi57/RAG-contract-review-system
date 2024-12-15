# !/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, request, jsonify
import threading
from flask_cors import CORS
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

os.environ["CUDA_VISIBLE_DEVICES"] = '0, 1,2,3,4,5,6,7'

app = Flask(__name__)
CORS(app)


# 加载模型
tokenizer = AutoTokenizer.from_pretrained("/data/DeepSeek67b", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("/data/DeepSeek67b", device_map="auto", trust_remote_code=True)

# 创建线程锁和计数器
lock = threading.Lock()
counter = 0
MAX_CONCURRENT_REQUESTS = 5  # 最大并发请求数


@app.route('/deepseek/conversation', methods=['POST'])
def conversation():
    global counter

    # 请求过载，返回提示信息
    if counter >= MAX_CONCURRENT_REQUESTS:
        return jsonify({'message': '请稍等再试'})

    # 获取线程锁
    with lock:
        counter += 1

    try:
        # 接收 POST 请求的数据
        question = request.json['question']
        question += '->'

        inputs = tokenizer(question, return_tensors='pt')
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
    app.run(host='0.0.0.0', port=8090)
