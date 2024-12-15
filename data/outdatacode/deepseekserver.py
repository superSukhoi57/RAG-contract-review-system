# !/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from transformers import AutoTokenizer, AutoModelForCausalLM
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


os.environ["CUDA_VISIBLE_DEVICES"] = '0,1,2,3,4,5,6,7'
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

try:
    # 检查是否有可用的GPU
    logger.info("cuda可用：{}".format(torch.cuda.is_available()))
    logger.info("GPU个数：{}".format(torch.cuda.device_count()))


    app = Flask(__name__)
    CORS(app)

    # 初始化分布式进程组
    dist.init_process_group(backend='nccl')

    # 设置 GPU 设备，LOCAL_RANK 参数用于指定当前进程在本地机器上的 GPU 设备 ID
    # python -m torch.distributed.launch --nproc_per_node=8 deepseekserver.py
    local_rank = int(os.environ['LOCAL_RANK'])
    torch.cuda.set_device(local_rank)

    logger.info("开始加载模型")
    # 加载模型
    tokenizer = AutoTokenizer.from_pretrained("/data/DeepSeek67b")
    model = AutoModelForCausalLM.from_pretrained("/data/DeepSeek67b")
    logger.info("模型加载完成")

    # 包装模型
    model = DDP(model, device_ids=[local_rank], output_device=local_rank)

    # 将模型移动到 GPU
    #device = torch.device("cuda", local_rank)
    #model.to(device)

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
            inputs = inputs.to(device)

            # 模型推理
            outputs = model.generate(**inputs)
            answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

            return jsonify({'answer': answer})

        finally:
            with lock:
                counter -= 1

    if __name__ == '__main__':
        print("Flask 服务器已启动")
        app.run(host='0.0.0.0', port=8090)

except Exception as e:
    logger.error(f"发生异常：{e}", exc_info=True)


