# Copyright (C) 2017 Kevin McKenzie.
#
# Code may not be copied, reused,  or modified in any way without written
# consent from Kevin McKenzie.

import logging
from models_fs import Album
from settings import init
from flask import (
    Flask,
    render_template,
    redirect
)

app = Flask(__name__)
init(app)

def render(path):
    if len(path) > 0:
        album = Album.get(path)
        if album is None:
            return redirect("./")
        photos = album.photos()
        context = {
            'album': album,
            'photos': photos
        }

        return render_template('album.html', context=context)

    albums = Album.active_albums()
    albums = [] if albums is None else albums

    context = {
        'albums': albums
    }

    return render_template('photography.html', context=context)

