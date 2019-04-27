# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging
from models_fs import Album, Image, User
from settings import init, ALLOWED_EXTENSIONS
import storage
from flask import (
    Flask,
    render_template,
    flash,
    request
)

app = Flask(__name__)
init(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file, album):
    folder = "albums/" + album + "/"
    img = None
    if album == "covers":
        folder = "covers/"
    if allowed_file(file.filename):
        saved_file_name = storage.upload_file(file, folder)
        img = Image(url=saved_file_name, album=album)
        img.put()
        flash('Uploaded photo to album %s' % album)
    else:
        flash('File extension not supported')
        raise Exception("File extension not supported")
    return img


def render():
    user = User.get("kjtmckenzie@gmail.com")

    if user is None and app.debug:
        admin = User("kjtmckenzie@gmail.com", firebaseID="kjtmckenzie@gmail.com", admin=True)
        admin.put()

    if not app.debug and (user is None or not user.admin):
        return 'Only admins can access this site', 401

    albums = Album.active_albums()

    if albums is None or len(albums) < 1:
        albums = []

    context = {
        'albums': albums
    }

    if request.method == 'POST':
        if "create-album" in request.form:
            try:
                title = request.form['album']
                location = request.form['location']
                path = request.form['path']
                if len(title) > 1:
                    new_album = Album(title, path, location=location)
                    new_album.put()
                    context['albums'] = context['albums'] + [new_album]
                    flash('New album %s created' % new_album)
            except Exception as e:
                flash('Album creation failed: %s' % e)

        if "upload-image" in request.form:
            try:
                uploaded_files = request.files.getlist("file")
                for file in uploaded_files:
                    if 'cover_image' in request.form:
                        img = upload_file(file, "covers")
                        album = Album.get(request.form['album'])
                        album.update_cover(img.url)
                    else:
                        upload_file(file, request.form['album'])

            except Exception as e:
                flash('Image upload failed: %s' % e)

    return render_template('admin.html', context=context)

