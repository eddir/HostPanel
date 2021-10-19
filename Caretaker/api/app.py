from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World! This is Flask.'


def run_flask():
    app.run(host='0.0.0.0', port=8000)
