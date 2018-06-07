# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging
import models
from google.appengine.ext import ndb

from flask import (
    Flask,
    render_template,
    flash
)

import flask
from settings import init

app = Flask(__name__)
init(app)

@app.route('/photography/', defaults={'path': ''})
@app.route('/photography/<path:path>')
def index(path):

    logging.info("Path is %s" % str(path))

    if len(path) > 0:
        logging.info("path: %s" % path)
        album = models.get_album_by_urlsafe(path)
        logging.info("album: %s" % str(album))
        logging.info("album.title: %s" % str(album.title))
        photos = models.get_album_photos(album.title)
        logging.info("photos: %s" % str(photos))
        context = {
            'album': album,
            'photos': photos
        }
        logging.info("returning with path")
        logging.info(str(context))

        return render_template('album.html', context=context)

    albums = models.get_active_albums()

    album_list = []

    for album in albums:
        album_dict = {}
        album_dict["album"] = album
        album_dict["cover"] = models.get_cover_image(album.title)
        album_dict["images"] = models.get_album_photos(album.title)
        album_dict["urlsafe"] = album.key.urlsafe()

        album_list.append(album_dict)

        logging.info("album list")
        logging.info(str(album_list))

    context = {
        'albums' : album_list
    }

    logging.info("context")
    logging.info(str(context))

    return render_template('photography.html', context=context)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error has occurred')

    return 'An error has occurred on the server', 500
