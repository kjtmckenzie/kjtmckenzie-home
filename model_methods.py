import logging
import google.api_core
from google.cloud import firestore
from settings import init
from retrying import retry
from flask import Flask

app = Flask(__name__)
init(app)
db = app.config['db']


def retry_if_service_unavailable_error(exception):
    """Return True if we should retry (in this case when it's an ServiceUnavailable), False otherwise"""
    return isinstance(exception, google.api_core.exceptions.ServiceUnavailable)


@retry(wait_exponential_multiplier=100,wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def get_user(email=None, firebaseID=None):
    user = None
    if email is not None:
        user = next(db.collection('Users').where('email', '==', email).get(), None)
    elif firebaseID is not None:
        user = next(db.collection('Users').where('firebaseID', '==', firebaseID).get(), None)
    if user is not None:
        user = user.to_dict()
    return user


@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def put_user(user):
    db.collection('Users').add(user)


@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def get_image(url):
    image = next(db.collection('Images').where('url', '==', url).get(), None)
    if image:
        image = image.to_dict()
    return image


@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def put_image(image):
    db.collection('Images').add(image)


@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def get_active_albums():
    all_albums = []
    album_generator = db.collection('Albums').where('active', '==', True).order_by('title').get()
    for album in album_generator:
        if album:
            album = album.to_dict()
            all_albums.append(album)
    return all_albums
    

@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def get_album(path):
    album = next(db.collection('Albums').where('path', '==', path).get(), None)
    if album:
        album = album.to_dict()
    return album


@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def get_album_images(path):
    image_gen = db.collection('Images').where('album', '==', path).order_by('url').get()
    images = []
    for image in image_gen:
        images.append(image.to_dict())
    return images


@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def put_album(album):
    db.collection('Albums').add(album)


@retry(wait_exponential_multiplier=100, wait_exponential_max=2000, retry_on_exception=retry_if_service_unavailable_error)
def update_cover(album):
    new_cover = album['cover']
    album = next(db.collection('Albums').where('path', '==', album['path']).get(), None)
    album_ref = db.collection('Albums').document(album.id)
    album_ref.update({'cover': new_cover})






