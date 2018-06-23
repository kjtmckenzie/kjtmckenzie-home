from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
import logging
import six


class GenericModel(ndb.Model):
    '''A generic ndb model that will hold common properties and methods.'''
    created_on = ndb.DateTimeProperty(auto_now_add=True, indexed=True)

    @classmethod
    def get(cls, identifier, ndb_class, ndb_attr=None):
        '''Search by key or urlsafe key'''

        if identifier is None:
            return None

        if (type(identifier) is ndb_class):
            return identifier
        if (type(identifier) is ndb.Key):
            if (str(identifier.kind()) + "<") in str(ndb_class):
                return identifier.get()
            return ndb_class.query(ndb_attr == identifier).get()
        if isinstance(identifier, six.string_types):
            try:
                # attempt to convert from URLsafe key
                return ndb.Key(urlsafe=identifier).get()
            except:
                return ndb_class.query(ndb_attr == identifier).get()

        return None



class User(GenericModel):
    '''Models an individual user'''
    email = ndb.StringProperty()
    admin = ndb.BooleanProperty(indexed=False, default=False)


    @classmethod
    def get(cls, user_id):
        '''Returns a user profile by email from the datastore'''

        user = GenericModel.get(user_id, User)
        if user is None and isinstance(user_id, six.string_types):
            return cls.query(cls.email == user_id).get()
        return user


    @classmethod
    def new(cls, email, admin=False):
        """Records a created user in the database.

        Args:
            email: the email address of the created user
            admin: a boolean flag indicating whether the user is a site admin

        Returns:
            The new user
        """
        if cls.get(email) is not None:
            logging.info("create_user failed.  User already exists: %s" % email)
            raise Exception("User already exists: %s" % email)
        user = cls(email=email, admin=admin)
        user.put()
        logging.info("User %s created.  Admin is %s" % (email, str(admin)))
        return user


    @classmethod
    def is_admin(cls, user_id):
        user = cls.get(user_id)
        if user is None:
            return False
        return user.admin


class Album(GenericModel):
    '''Models an individual album of images'''
    title = ndb.StringProperty()
    active = ndb.BooleanProperty(default=True)
    location = ndb.StringProperty()

    @classmethod
    def get(cls, album_id):
        '''Get an album.  Also creates the covers album if it
           doesn't already exist'''
        album = GenericModel.get(album_id, cls, ndb_attr=cls.title)
        # create the covers album if it hasn't already been created
        if album is None and album_id == "covers":
            album = Album(title=album, location="None")
            logging.info("Creating the covers album for the first time")
            album.put()
        return album


    @classmethod
    def photos(cls, album_id):
        '''Return all photos from the provided album'''
        album = Album.get(album_id)
        try:
            return Image.query(Image.album == album.key)\
                .order(Image.filename).fetch()
        except:
            return None

    @classmethod
    def active_albums(cls, return_covers=False):
        '''Returns all active albums.'''
        albums = cls.query(cls.active == True)

        # don't return the covers album unless specifically requested
        if not return_covers:
            albums = albums.filter(cls.title != "covers")
        return albums.order(cls.title).fetch()


    @classmethod
    def new(cls, title, location):
        '''Creates a new album with title and location'''
        if cls.get(title) is not None:
            logging.info("create_album failed.  Album already exists: %s" % title)
            raise Exception("Album already exists: %s" % title)
        album = cls(title=title, location=location)
        album.put()
        logging.info("Album %s created.  Location is %s" % (title, location))
        return album


class Image(GenericModel):
    '''Models an individual image'''
    album = ndb.KeyProperty(kind=Album)
    url = ndb.StringProperty()
    blobstore_key = ndb.BlobProperty()
    filename = ndb.StringProperty(indexed=True)

    @classmethod
    def get(cls, image_id):
        '''Get an image by calling the generic get function'''
        return GenericModel.get(image_id, cls, ndb_attr=cls.url)

    @classmethod
    def new(cls, url, album, filename):
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
                    album=Album.get(album).key,
                    blobstore_key=blob_key,
                    filename=filename)
        img.put()
        logging.info("Image %s uploaded to album %s" % (filename, album))
        return img


class CoverImage(GenericModel):
    '''Models the record of album cover images'''
    album = ndb.KeyProperty(kind=Album)
    cover_image = ndb.KeyProperty(kind=Image)

    @classmethod
    def get(cls, album_id):
        '''Return the cover image for an album'''
        # get the cover image record and if it exists, query for the image
        logging.info("Getting album ID: %s" % album_id)
        coverImage = GenericModel.get(Album.get(album_id).key,
                                      cls,
                                      ndb_attr=cls.album)
        if coverImage == None:
            return None
        return GenericModel.get(coverImage.cover_image, Image)


    @classmethod
    def new(cls, image_id, album_id):
        '''Set the cover image of an album'''
        album = Album.get(album_id)
        image = Image.get(image_id)
        cover_image = cls.get(album_id)

        # first check to see if the cover image record already exists
        if cover_image:
            # update the existing cover image
            cover_image.cover_image = image.key
        else:
            # create a new cover image
            cover_image = CoverImage(album=album.key, cover_image=image.key)

        cover_image.put()
        logging.info("Cover image %s saved to album %s" % (image.filename, album.title))
        return cover_image