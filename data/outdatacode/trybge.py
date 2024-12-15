
# 加载预训练模型
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('/data/dataEmbedding/bge-large-zh',device='cuda')

print("Max Sequence Length:", model.max_seq_length)
# Change the length to 200
model.max_seq_length = 200
print("After Change Max Sequence Length:", model.max_seq_length)
# 不能将长度增加到高于相应 transformer 模型的最大支持长度

message="你好！"

example=model.encode(message)# 是一个列表
print("type of model.encode() %s ; model.encode=%r",type(example),example)
print("demension of model.encode() %s",len(example))

example=model.encode(message)[0]# 取第一个元素作为向量
print("type of model.encode()[0] %s ; model.encode()[0]=%r",type(example),example)

example=model.encode(message)[0].tolist()
print("type of model.encode()[0].tolist %s ; model.encode()[0].tolist=%r",type(example),example)
example=model.encode(message)[0].shape
print("type of model.encode()[0].shape %s ; model.encode()[0].shape=%r",type(example),example)
