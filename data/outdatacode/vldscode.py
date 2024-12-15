import os
from vllm import LLM

# 设置环境变量
os.environ["TOKENIZERS_PARALLELISM"] = "false"

print("开始加载模型")
llm = LLM("/data/deepseekcode",  dtype="half")
print("模型加载完成")

outputs = llm.generate("你好，现在几点了？")
# 解析输出
output_text = outputs[0].outputs[0].text
print(output_text)