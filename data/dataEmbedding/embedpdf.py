from langchain.document_loaders import PyPDFLoader
# Load a PDF document
file_path = "/data/dataEmbedding/demo.pdf"
loader = PyPDFLoader(file_path)
documents = loader.load()

# 切割文本
from langchain.text_splitter import RecursiveCharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

# 打印前2个文本块
# for chunk in chunks[:2]:    
#     print(chunk)
print("chunks的类型是：", type(chunks))
print("chunk的类型是：",type(chunks[0]))
print("第一个分片chunk：",chunks[0].page_content)


# 加载预训练模型
from sentence_transformers import SentenceTransformer
import time
model = SentenceTransformer('/data/dataEmbedding/bge-large-zh')

startTime = time.time()
print("测试模型是否加载成功：",model.encode(["你好"]))
endTime = time.time()
print("测试模型加载时间(没GPU加速)：",endTime-startTime)


import torch
device = torch.device("cuda")
model = model.to(device)
startTime = time.time()
print("使用gpu加速：",model.encode(["正在是使用GPU加速"]))
endTime = time.time()
print("使用gpu加速时间：",endTime-startTime)


#langchain对milvus没有直接的接口可以使用beg-large-zh模型，所以需要自己写一个
from pymilvus import MilvusClient
# 1. 设置Milvus客户端
client = MilvusClient(
    uri='http://10.14.1.2:19530'
)
# 2. 创建集合
# client.create_collection(
#     collection_name="quick_setup",
#     dimension=5,
# )
for chunk in chunks:
    #print(chunk)测试过，chunk和chunk.page_content都是字符串
    mydata={
        "vector":model.encode([chunk.page_content])[0].tolist(),
        "text":chunk.page_content
    }
    # 3. 插入实体到集合中
    res = client.insert(
        collection_name="demo",
        data=mydata
    )
 
print(res)

# 4.关闭连接    
client.close()


