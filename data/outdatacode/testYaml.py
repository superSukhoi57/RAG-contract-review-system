import yaml

def read_yaml_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# 读取配置文件
config = read_yaml_config('./application.yaml')

# 访问配置项
print(config['milvus']['host'])  
print(config['server']['port'])  