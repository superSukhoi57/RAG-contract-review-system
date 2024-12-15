根目录里面的文件：
test.py：是测试用的
simpleServer.py是一个简单的使用大模型的服务器，监听一个端口
predict.py：是测试大模型能不能使用的。
getPdfFromHttp.py：是测试能不能从http请求里面获取pdf，然后对其分片并且组成json模板。

进入Milvus里面运行docker-compose  start
embedcreatecollection.py：是用来创建milvus的集合的
embedpdf.py：是用来加载pdf然后分片嵌入milvus的
signalquery.py：是单向量查询
embedquery.py：是多向量查询
embedtest.py：是测试文档分片的。

	

blueprint.py和views是一个完整的服务，可以通过api实现操作milvus的插件collection和上传文档分片，存进数据库。端口是8800