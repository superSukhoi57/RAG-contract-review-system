from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

mdir = "/data/DeepSeek67b"
tokenizer = AutoTokenizer.from_pretrained(mdir, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(mdir, trust_remote_code=True).cuda()
input_text = "写一个快排算法"
inputs = tokenizer(input_text, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_length=128)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
