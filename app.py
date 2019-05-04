from flask import Flask, request, render_template, send_from_directory, redirect, url_for
import os
from time import time as cur_time_secs
from dbmngr import DBManager
from werkzeug.utils import secure_filename
import threading
from file_sched import file_scheduler_mainloop
from sqlite3 import OperationalError


app = Flask(__name__)
app.config['SECRET_KEY'] = 'abc'
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'upload_folder')
ALLOWED_EXTENSIONS = {'txt', }


def is_allowed_filename(filename):
    return filename.split('.')[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        delay = request.values['exp_delay']
        if is_allowed_filename(file.filename):
            db = DBManager('file_data.db')
            filename = secure_filename(file.filename)
            if db.is_file_exists(filename):
                return render_template('index.html', allowed_ext=ALLOWED_EXTENSIONS,
                                       exist_msg='File with such name already exists')
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            exp_date = cur_time_secs() + int(delay)
            db.insert_data(filename, exp_date)
        else:
            return render_template('index.html', allowed_ext=ALLOWED_EXTENSIONS, exist_msg='')
    return render_template('index.html', allowed_ext=ALLOWED_EXTENSIONS, exist_msg='')


@app.route('/search', methods=['GET'])
def search():
    if request.values:
        db = DBManager('file_data.db')
        status = db.search_on_filename(request.values['filename'])
        if status:
            return render_template('search.html', search_status=status,
                               download_link=f"/download?filename={request.values['filename']}",
                               download_text='Download here',
                               observe_link=f"/observe?filename={request.values['filename']}",
                               observe_text='Inspect file')
        else:
            return render_template('search.html', search_status=status)
    return render_template('search.html')


@app.route('/observe', methods=['GET'])
def observe():
    if request.values:
        filename = request.values['filename']
        db = DBManager('file_data.db')
        status = db.is_file_exists(filename)
        if status:
            exp_time = db.get_exp_time(filename)
            return render_template('file_observer.html', filename=filename, time_to_death=(exp_time - cur_time_secs()))
        else:
            return "<h1>404</h1><p>file was not found</p>"
    else:
        return redirect(url_for('index'))


@app.route('/download')
def send_file_handle():
    if request.values:
        filename = request.values['filename']
        try:
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename=filename, as_attachment=True,
                                       attachment_filename=filename)
        except Exception as e:
            print(str(e))
    else:
        return redirect(url_for('index'))


def _ensure_database_existence(path):
    db = DBManager(path)
    try:
        q = """select * from exp_dates limit 1"""
        db.conn.execute(q)
    except OperationalError:
        db.conn.execute("create table exp_dates (filename text, exp_date integer)")



if __name__ == '__main__':
    _ensure_database_existence('file_data.db')
    PORT = os.environ.get('PORT', 8000)
    t2 = threading.Thread(target=file_scheduler_mainloop, args=('file_data.db', './upload_folder'), kwargs={'delay': 10})
    t2.start()
    app.run(host='0.0.0.0', port=PORT, debug=True, use_reloader=False)
