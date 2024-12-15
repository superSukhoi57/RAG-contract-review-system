from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("/home/baichuan2-7b/Baichuan2-7B-Chat", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("/home/baichuan2-7b/Baichuan2-7B-Chat", device_map="auto", trust_remote_code=True)
inputs = tokenizer('登鹳雀楼->王之涣 \
        夜雨寄北->', return_tensors='pt')
inputs = inputs.to('cuda:0')
pred = model.generate(**inputs, max_new_tokens=64,repetition_penalty=1.1)
print(tokenizer.decode(pred.cpu()[0], skip_special_tokens=True))


