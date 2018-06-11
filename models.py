from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
import logging


def get_user(email):
    '''Returns a user profile by email from the datastore'''
    return User.query(User.email == email).get()


def is_admin(email):
    '''Return True if a user exists and is an admin, otherwise False'''
    user = get_user()
    if user is None:
        return False
    return user.admin


def create_user(email, admin=False):
    """Records a created user in the database.

    Args:
        email: the email address of the created user
        admin: a boolean flag indicating whether the user is a site admin

    Returns:
        The new user
    """
    if get_user(email) is not None:
        logging.info("create_user failed.  User already exists: %s" % email)
        raise Exception("User already exists: %s" % email)
    user = User(email=email, admin=admin)
    user.put()
    logging.info("User %s created.  Admin is %s" % (email, str(admin)))
    return user


def create_album(title, location):
    '''Creates a new album with title and location'''
    if get_album(title) is not None:
        logging.info("create_album failed.  Album already exists: %s" % title)
        raise Exception("Album already exists: %s" % title)
    album = Album(title=title, location=location)
    album.put()
    logging.info("Album %s created.  Location is %s" % (title, location))
    return album


def get_active_albums(return_covers=False):
    '''Returns all active albums.'''
    albums = Album.query(Album.active == True)

    # don't return the covers album unless specifically requested
    if not return_covers:
        albums = albums.filter(Album.title != "covers")
    return albums.order(Album.title).fetch()


def get_album(album_title):
    '''Get an album by its album title.  Also creates the covers album if it
       doesn't already exist'''
    album = Album.query(Album.title == album_title).get()

    # create the covers album if it hasn't already been created
    if album is None and album_title == "covers":
        album = Album(title=album_title, location="None")
        logging.info("Creating the covers album for the first time")
        album.put()
    return album


def get_album_by_urlsafe(urlsafe):
    '''Return an album by the urlsafe key'''
    return Album.query(Album.key == ndb.Key(urlsafe=urlsafe)).get()


def set_cover_image(img, album_title):
    '''Set the cover image of an album'''
    album = get_album(album_title)

    # first check to see if the cover image record already exists
    cover_image = CoverImage.query(CoverImage.album == album.key).get()

    if cover_image:
        # update the existing cover image
        cover_image.cover_image = img.key
    else:
        # create a new cover image
        cover_image = CoverImage(album=album.key, cover_image = img.key)

    cover_image.put()
    return cover_image


def get_cover_image(album_title):
    '''Return the cover image for an album'''
    album = get_album(album_title)

    # get the cover image record and if it exists, query for the image
    cover_image_obj = CoverImage.query(CoverImage.album == album.key).get()
    if cover_image_obj is None:
        return None
    return Image.query(Image.key == cover_image_obj.cover_image).get()


def get_album_photos(album_title):
    '''Return all photos from the provided album'''
    album = get_album(album_title)
    try:
        return Image.query(Image.album == album.key).order(Image.filename)\
            .fetch()
    except:
        return None


def add_photo_to_album(url, album, filename):
    """Records an uploaded image in the database.

    Args:
        url: the file path for the image in Google Cloud Storage.
        album: an album for the image.
        filename: the name of the file being uploaded (for sorting purposes)

    Returns:
        The image that was saved.
    """
    blobstore_filename = '/gs{}'.format(url)
    blob_key = blobstore.create_gs_key(blobstore_filename)

    # serving URLs are for the images API and they allow dynamic scaling
    url = images.get_serving_url(blob_key, secure_url=True)

    # record the image in the database
    img = Image(url=url,
                album=get_album(album).key,
                blobstore_key=blob_key,
                filename=filename)
    img.put()
    logging.info("Image %s uploaded to album %s" % (filename, album))
    return img


class GenericModel(ndb.Model):
    '''A generic ndb model that will hold common properties and methods.'''
    created_on = ndb.DateTimeProperty(auto_now_add=True, indexed=True)


class User(GenericModel):
    '''Models an individual user'''
    email = ndb.StringProperty()
    admin = ndb.BooleanProperty(indexed=False, default=False)


class Album(GenericModel):
    '''Models an individual album of images'''
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
    '''Models the record of album cover images'''
    album = ndb.KeyProperty(kind=Album)
    cover_image = ndb.KeyProperty(kind=Image)

