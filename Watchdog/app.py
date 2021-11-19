from flask import Flask

from views import status, logs

app = Flask(__name__)

app.add_url_rule('/', view_func=status.ping)
app.add_url_rule('/stat/', view_func=status.stat)
app.add_url_rule('/status/', view_func=status.status)
app.add_url_rule('/logs/', view_func=logs.list_logs)
app.add_url_rule('/logs/download/<log_file>/', view_func=logs.get_log)
app.add_url_rule('/logs/remove/<log_file>/', view_func=logs.remove_log, methods=['POST'])


def run_flask(port, debug=False):
    app.run(host='0.0.0.0', port=port, debug=debug)
