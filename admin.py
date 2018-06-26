# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging

from flask import (
    Flask,
    render_template,
    flash,
    request
)

import storage

import flask

from models import Image, Album, CoverImage
from settings import init

app = Flask(__name__)
init(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file(file, album):
    folder = "photography/" + album
    img = None
    if album == "covers":
        folder = "covers"
    if allowed_file(file.filename):
        saved_file_name = storage.upload_file_to_gcs(file, folder)
        img = Image.new(url=saved_file_name, album=album, filename=file.filename)
        flash('Uploaded photo to album %s' % album)
    else:
        flash('File extension not supported')
        raise Exception("File extension not supported")
    return img


@app.route('/admin/', methods=['POST', 'GET'])
def admin():
    user = models.User.get(users.get_current_user().email())

    if user is not None and not user.admin:
        return 'Only admins can access this site', 401

    albums = Album.active_albums()

    if albums is None or len(albums) < 1:
        albums = []

    context = {
        'user_email': user.email,
        'albums': albums
    }

    if request.method == 'POST':
        if "create-album" in request.form:
            try:
                album = request.form['album']
                location = request.form['location']
                if len(album) > 1:
                    new_album = Album.new(album, location)
                    context['albums'] = context['albums'] + [new_album]
                    flash('New album %s created' % album)
            except Exception as e:
                flash('Album creation failed: %s' % e)

        if "upload-image" in request.form:
            try:
                uploaded_files = flask.request.files.getlist("file")
                for file in uploaded_files:
                    if 'cover_image' in request.form:
                        img = upload_file(file, "covers")
                        CoverImage.new(img, request.form['album'])
                    else:
                        upload_file(file, request.form['album'])

            except Exception as e:
                flash('Image upload failed: %s' % e)

    return render_template('admin.html', context=context)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error has occurred')

    return 'An error has occurred on the server', 500
