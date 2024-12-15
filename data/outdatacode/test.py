from flask import Flask

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return 'successful'

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True, port=8899)
