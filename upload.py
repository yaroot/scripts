#!/usr/bin/env python3

from flask import Flask, request, redirect, url_for
import os

_UPLOAD_DIR = os.environ.get("UPLOAD_DIR")
if not _UPLOAD_DIR:
    _UPLOAD_DIR = os.path.join(os.environ['HOME'], '.local', 'uploads')

app = Flask(__name__)

UPLOAD_HTML = """
<form enctype="multipart/form-data" method="post" action="/">
<input type="file" name="files" multiple />
<input type="submit" value="upload"/>
</form>
"""


def render_list_dir(files):
    return ''.join(['%s\n<br>' % f for f in files])


def strip_left(orig, target):
    if orig.startswith(target):
        return orig[len(target) + 1:]
    else:
        return orig


def walk_upload_dir(base):
    for dirpath, dirnames, filenames in os.walk(base):
        for f in filenames:
            yield strip_left(os.path.join(dirpath, f), base)


def save_file(f):
    save_path = os.path.join(_UPLOAD_DIR, f.filename)
    if not os.path.exists(save_path):
        f.save(save_path)


@app.route('/', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    for f in files:
        save_file(f)
    import ipdb; ipdb.set_trace()
    return redirect(url_for('index'))


@app.route("/")
def index():
    file_list = list(walk_upload_dir(_UPLOAD_DIR))
    return UPLOAD_HTML + '\n<hr>\n' + render_list_dir(file_list)


if __name__ == '__main__':
    app.run(debug=True)
