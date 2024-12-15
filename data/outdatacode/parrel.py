from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
model_name = "/data/DeepSeek67b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
max_memory_mapping = { 0:"24GB",1:"32GB",2:"32GB",3:"32GB",4:"32GB",5:"32GB",6:"32GB",7:"32GB" } 
# load model in 4-bit
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

model= AutoModelForCausalLM.from_pretrained(model_name, max_memory = max_memory_mapping,quantization_config=quantization_config ).to("cuda")

prompt = "Hello, my llama is cute"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
generated_ids = model.generate(**inputs)
outputs = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)