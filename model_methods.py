import logging
import six
import base64
from google.cloud import firestore
from settings import init

from flask import Flask

app = Flask(__name__)

init(app)
db = app.config['db']


def get_user(email):
    user = next(db.collection('Users').where('email', '==', email).get(), None)
    if user is not None:
        user = user.to_dict()
    return user


def put_user(user):
    db.collection('Users').add(user)


def get_image(url):
    image = next(db.collection('Images').where('url', '==', url).get(), None)
    if image:
        image = image.to_dict()
    return image


def put_image(image):
    db.collection('Images').add(image)


def get_active_albums():
    all_albums = []
    album_generator = db.collection('Albums').where('active', '==', True).get()
    for album in album_generator:
        if album:
            album = album.to_dict()
            all_albums.append(album)
    return all_albums
    

def get_album(path):
    album = next(db.collection('Albums').where('path', '==', path).get(), None)
    if album:
        album = album.to_dict()
    return album


def get_album_images(path):
    image_gen = db.collection('Images').where('album', '==', path).get()
    images = []
    for image in image_gen:
        images.append(image.to_dict())
    return images


def put_album(album):
    db.collection('Albums').add(album)


def update_cover(album):
    new_cover = album['cover']
    album = next(db.collection('Albums').where('path', '==', album['path']).get(), None)
    album_ref = db.collection('Albums').document(album.id)
    album_ref.update({'cover': new_cover})






