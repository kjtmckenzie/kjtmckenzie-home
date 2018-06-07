from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
import logging
import six
import random
from datetime import datetime, timedelta

import cloudstorage as gcs


def get_user(email):
    return User.query(User.email == email).get()


def is_admin(email):
    user = get_user()
    if user is None:
        raise Exception("User does not exist: %s" % email)
    return user.admin

def create_user(email, admin=False):
    if get_user(email) is not None:
        raise Exception("User already exists: %s" % email)
    user = User(email=email, admin=admin)
    user.put()


def create_album(title, location):
    if get_album(title) is not None:
        raise Exception("Album already exists: %s" % title)
    album = Album(title=title, location=location)
    album.put()
    return album


def get_active_albums(return_covers=False):
    albums = Album.query(Album.active == True)
    if not return_covers:
        albums = albums.filter(Album.title != "covers")
    return albums.order(Album.title).fetch()


def get_album(album_title):
    album = Album.query(Album.title == album_title).get()
    if album is None and album_title == "covers":
        album = Album(title=album_title, location="None")
        album.put()
    return album

def get_album_by_urlsafe(urlsafe):
    return Album.query(Album.key == ndb.Key(urlsafe=urlsafe)).get()


def set_cover_image(img, album_title):
    album = get_album(album_title)

    try:
        cover_image = CoverImage.query(CoverImage.album == album.key).get()
    except:
        cover_image = None

    if cover_image:
        cover_image.cover_image = img.key
    else:
        cover_image = CoverImage(album=album.key, cover_image = img.key)

    cover_image.put()
    return cover_image


def get_cover_image(album_title):
    album = get_album(album_title)
    cover_image_obj = CoverImage.query(CoverImage.album == album.key).get()
    if cover_image_obj is None:
        return None
    return Image.query(Image.key == cover_image_obj.cover_image).get()


def get_album_photos(album_title):
    album = get_album(album_title)
    try:
        return Image.query(Image.album == album.key).order(Image.filename).fetch()
    except:
        return None


def add_photo_to_album(url, album, filename):
    """Records an uploaded image in the database.

    Args:
        url: the file path for the image in Google Cloud Storage.
        album: an album for the image.

    Returns:
        The image that was saved.
    """

    blobstore_filename = '/gs{}'.format(url)
    blob_key = blobstore.create_gs_key(blobstore_filename)
    url = images.get_serving_url(blob_key, secure_url=True)
    img = Image(url=url, album=get_album(album).key, blobstore_key=blob_key, filename=filename)
    img.put()
    return img


class GenericModel(ndb.Model):
    '''A generic ndb model that will hold common properties and methods. '''
    created_on = ndb.DateTimeProperty(auto_now_add=True, indexed=True)

class User(GenericModel):
    '''Models an individual user'''
    email = ndb.StringProperty()
    admin = ndb.BooleanProperty(indexed=False, default=False)


class Album(GenericModel):
    '''Models an individual user'''
    title = ndb.StringProperty()
    active = ndb.BooleanProperty(default=True)
    location = ndb.StringProperty()


class Image(GenericModel):
    '''Models an individual image'''
    album = ndb.KeyProperty(kind=Album)
    url = ndb.StringProperty()
    blobstore_key = ndb.BlobProperty()
    filename = ndb.StringProperty(indexed=True)


class CoverImage(GenericModel):
    album = ndb.KeyProperty(kind=Album)
    cover_image = ndb.KeyProperty(kind=Image)




