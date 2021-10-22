import getpass
import json
import os
import uuid
from os import listdir
from os.path import isfile, join
from pathlib import Path

from flask import Flask, send_from_directory, abort, request

app = Flask(__name__)


@app.route('/')
def hello():
    return str(getpass.getuser())


@app.route('/logs/')
def list_logs():
    """
    Возвращает список доступных для скачивания логов с указанием их размера
    :return:
    """
    path = os.path.join(str(Path.home()), "HostPanel")
    files = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith("log")]

    logs = []
    for f in files:
        logs.append({
            'name': f,
            'size': os.path.getsize(os.path.join(str(Path.home()), "HostPanel", f))
        })

    return json.dumps(logs)


@app.route('/logs/download/<log_file>/')
def get_log(log_file):
    """
    Возвращает файл лога по заданному имени, размеру в MB и отступу
    :return:
    """
    try:
        # отправить команду на разбиение логов и помощение их в папку %flask_app%/static/logs/log%date%/

        chunk_size = request.args.get('size')
        chunk_number = request.args.get('number')

        if chunk_size is None:
            raise ValueError('Size must be set')

        if chunk_number is None:
            raise ValueError('Number must be set')

        chunk_size = int(chunk_size)
        chunk_number = int(chunk_number)

        # от 0 до терабайта
        if not 0 < chunk_size < 2 ** 20:
            raise AssertionError("Размер файла не должен превышать терабайта или меньше мегабайта.")

        if not 0 < chunk_number < 1000:
            raise AssertionError("Номер части от 0 до 1000.")

        chunk_number = str(chunk_number-1).rjust(3, "0")

        log_path = os.path.join(str(Path.home()), "HostPanel", log_file)
        output_dir = os.path.join(str(Path.home()), "HostPanel", "Caretaker", "api", "static", uuid.uuid4().hex)
        output_path = os.path.join(output_dir, log_file)

        if not isfile(log_path):
            raise AssertionError("Указанный файл не найжен.")

        os.system("mkdir -p {3} && "
                  "split --bytes {0}M --numeric-suffixes --suffix-length=3 {1} {2}.".
                  format(chunk_size, log_path, output_path, output_dir))

        # continue HERE: создаём папку для хранения кусочков, отдаём нужный кусочек пользователю и удаляем лишнее
        # чтобы удалить файл, отправляем его в файлик с указанием пути и даты удаления. При каждом реквесте проверять
        # нет ли файлов к удалению и удалять, если есть.

        if not os.path.isfile(str(output_path) + "." + str(chunk_number)):
            raise AssertionError("Не удалось извлечь указанную часть. Файл меньшего размера.")

        return send_from_directory(output_dir, log_file+"."+chunk_number, as_attachment=True)
    except FileNotFoundError:
        abort(404)
    except Exception as e:
        return str(e)


@app.route('/logs/remove/<log_file>/', methods=['POST'])
def remove_log(log_file):
    """
    Удаляет указанный лог
    :return:
    """
    location = os.path.join(str(Path.home()), "HostPanel", log_file)
    if isfile(location):
        os.remove(location)

    return "ok"


def run_flask(port, debug=False):
    app.run(host='0.0.0.0', port=port, debug=debug)
