from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World! This is Flask.'


def run_flask():
    app.run(port=8080, debug=True)
