import os
import path_helper  # Sets PYTHONPATS for current project.
from src import main
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, flash, redirect, url_for, Markup
from data_utils import clean_single_text_document, insert_one_to_db


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
RAW_UPLOAD_FOLDER = 'upload\\raw'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = RAW_UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.secret_key = 'random string'
app.debug = False
app.use_reloader = False


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('form.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == "POST":
        query = request.form.get('search') if request.form.get('search') else 'nice try, won\'t break!'
        model = request.form.get('model') if request.form.get('model') else 'tfidf'
        metric = request.form.get('metric') if request.form.get('metric') else 'minkowski'
        topk = int(request.form.get('topk')) if request.form.get('topk') else 10
        print('Search parameters: query=[{}], model=[{}], metric=[{}], topk=[{}]'.format(query, model, metric, topk))
        results = main.search(query, model, metric, topk)
        cursor = main.get_topk_docs_from_db(results)
        res = list()
        for rank, doc_object in enumerate(cursor):
            res.append(
                (
                    str(rank + 1),
                    doc_object['title'],
                    doc_object['path'],
                    doc_object['text'][100:400]
                )
            )
        return render_template("results.html", q=query, results=res)
    else:
        return "ERROR"


# @app.route('/upload')
# @app.route('/upload.html')
# def upload():
#     return render_template('upload.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        target = os.path.join(APP_ROOT, RAW_UPLOAD_FOLDER)
        # If path doesn't exist, create it
        if not os.path.isdir(target):
            os.mkdir(target)

        for file in request.files.getlist("file"):
            filename = secure_filename(file.filename)
            stemmed_filename = filename[:len(filename) - 4]
            destination = "\\".join([target, filename])
            # print(destination)

            try:
                print('Copying file to upload\\raw.')
                if not Path.is_file(Path(destination)):
                    file.save(destination)
                else:
                    print('File has already been added to database. Exiting.')
                    exit(1)
            except IOError:
                print('Destination must be writable.')
                exit(-1)
            text = clean_single_text_document(destination)
            print(stemmed_filename)
            print(destination)
            print(text)
            insert_one_to_db(stemmed_filename, destination, text)
        message = Markup('File(s) added to database <strong>successfully</strong>.')
        flash(message)
        return redirect(url_for('index'))
    else:
        return 'Illegal access!'


if __name__ == '__main__':
    app.run(debug=True)
