# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging
from models_fs import Album, Image, User
import storage
import os

from flask import (
    Flask,
    render_template,
    flash,
    request,
    send_from_directory
)

from settings import init, ALLOWED_EXTENSIONS

app = Flask(__name__)
init(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file(file, album):
    folder = "photography/" + album
    img = None
    if album == "covers":
        folder = "covers"
    if allowed_file(file.filename):
        saved_file_name = storage.upload_file(file, folder)
        img = Image(url=saved_file_name, album=album)
        img.put()
        flash('Uploaded photo to album %s' % album)
    else:
        flash('File extension not supported')
        raise Exception("File extension not supported")
    return img


@app.route('/admin/', methods=['POST', 'GET'])
def admin():
    #user = User.get(users.get_current_user().email())
    #TODO

    user = User.get("kjtmckenzie@gmail.com")

    if user is None and app.debug:
        admin = User("kjtmckenzie@gmail.com", admin=True)
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
                        print("request.form['album'] = %s" %
                              str(request.form['album']))
                        album = Album.get(request.form['album'])
                        album.set_cover(img.url)
                        album.put()
                    else:
                        upload_file(file, request.form['album'])

            except Exception as e:
                flash('Image upload failed: %s' % e)

    return render_template('admin.html', context=context)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    
    albums = Album.active_albums()

    if albums is None or albums == []:
        Album(title="Test 1", path="test-1", location="Test location 1").put()
        Album(title="Test 2", path="test-2", location="Test location 2").put()
        albums = Album.active_albums()

    albums = [] if albums is None else albums

    context = {
        'albums' : albums
    }

    return render_template('index.html', context=context)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error has occurred')

    return 'An error has occurred on the server', 500



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
