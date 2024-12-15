from pymilvus import MilvusClient, FieldSchema, CollectionSchema, DataType
import yaml

# 读取配置文件，使用绝对路径，以免出现找不到文件的情况
with open('/data/baichuan2-7b/views/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

class MilvusLink:
    client = None

    @classmethod
    def initialize(cls):
        cls.client = MilvusClient( uri=config['milvus']['uri'])

# 在模块加载时（就是在被import时）自动调用 initialize 方法
MilvusLink.initialize()
