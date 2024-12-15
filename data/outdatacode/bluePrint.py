from flask import Flask
from views.CollectionHandler import collectionhandler
from views.DocHandler import dochandler
#from .views import blueprint2
app = Flask(__name__)
# 注册蓝图
app.register_blueprint(collectionhandler)
app.register_blueprint(dochandler)
#app.register_blueprint(blueprint2)
if __name__ == '__main__':
    print("Flask 服务器已启动")
    app.run(host='0.0.0.0', port=8800)
