import os
import torch
from torch.nn.parallel import DistributedDataParallel as DDP
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from accelerate import init_empty_weights, init_empty_weights, load_checkpoint_and_dispatch

from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import logging

# 设置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["CUDA_VISIBLE_DEVICES"] = '0,1,2,3,4,5,6,7'
# 获取当前进程的 GPU ID (LOCAL_RANK)，默认为 0
local_rank = int(os.getenv('LOCAL_RANK', 0))

# 将当前进程绑定到指定 GPU
torch.cuda.set_device(local_rank)

try:
    # 检查是否有可用的 GPU
    logger.info(f"cuda 可用：{torch.cuda.is_available()}")
    logger.info(f"GPU 数量：{torch.cuda.device_count()}")

    # Flask 应用初始化
    app = Flask(__name__)
    CORS(app)

    # 分布式进程组初始化
    torch.distributed.init_process_group(backend='nccl')

    # 获取本地进程的 GPU ID
    local_rank = int(os.environ['LOCAL_RANK'])
    torch.cuda.set_device(local_rank)

    logger.info("开始加载模型")

       # 使用 init_empty_weights 优化大模型初始化
    with init_empty_weights():
        model = AutoModelForCausalLM.from_pretrained(
            "/data/DeepSeek67b", trust_remote_code=True
        )

    # 使用 load_checkpoint_and_dispatch 正确加载权重并分发到多个 GPU
    model = load_checkpoint_and_dispatch(
        model,
        "/data/DeepSeek67b",
        device_map="balanced_low_0",  # 根据 GPU 显存自动分配
        no_split_module_classes=["BloomBlock"]  # 避免分片某些模块
    )

    # 加载 Tokenizer
    tokenizer = AutoTokenizer.from_pretrained("/data/DeepSeek67b")

    logger.info("模型加载完成")
    logger.info(f"模型分配情况: {model.hf_device_map}")

    # 控制并发请求数量
    lock = threading.Lock()
    counter = 0
    MAX_CONCURRENT_REQUESTS = 5

    @app.route('/deepseek/conversation', methods=['POST'])
    def conversation():
        global counter

        # 请求过载处理
        if counter >= MAX_CONCURRENT_REQUESTS:
            return jsonify({'message': '请稍等再试'})

        with lock:
            counter += 1

        try:
            # 获取用户请求数据
            question = request.json['question'] + '->'

            # Tokenize 输入
            inputs = tokenizer(question, return_tensors='pt').to('cuda')

            # 推理
            outputs = model.generate(**inputs)
            answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

            return jsonify({'answer': answer})

        finally:
            with lock:
                counter -= 1

    if __name__ == '__main__':
        logger.info("Flask 服务器已启动")
        app.run(host='0.0.0.0', port=8090)

except Exception as e:
    logger.error(f"发生异常：{e}", exc_info=True)

# torchrun --nproc_per_node=8 tensorparrel.py

