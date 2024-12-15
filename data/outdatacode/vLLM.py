from vllm import LLM
print("开始加载模型")
llm = LLM("/data/DeepSeek67b", tensor_parallel_size=8, dtype="half")
print("模型加载完成")

output = llm.generate("你好，现在几点了？")
# 解析输出
output = llm.tokenizer.decode(output[0], skip_special_tokens=True)
print(output)