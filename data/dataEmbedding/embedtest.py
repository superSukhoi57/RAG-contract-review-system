from langchain.document_loaders import PyPDFLoader

# Load a PDF document
file_path = "/home/baichuan2-7b/dataEmbedding/demo.pdf"
loader = PyPDFLoader(file_path)
documents = loader.load()

# 切割文本
from langchain.text_splitter import CharacterTextSplitter
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

# 打印前2个文本块
for chunk in chunks[:1]:
    print(chunk)
print(type(chunks))
print(type(chunks[1]))

print("===================================================================")

for chunk2 in chunks[:2]:
    print(chunk2)
