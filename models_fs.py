import logging
import model_methods

cover_title = "covers"


class GenericModel(object):
    '''Base class for a model in the database'''

    def to_dict(self):
        return vars(self)

    def __repr__(self):
        repr_str = "%s(" % type(self).__name__
        model_dict = vars(self)

        if len(model_dict) < 1:
            return repr_str + ")"

        for field in model_dict.keys():
            repr_str = repr_str + "%s=%s, " % (field, model_dict[field])

        repr_str = repr_str[:-2] + ")"

        return repr_str
        

class User(GenericModel):
    """
    Represents a user that authenticates into the system.  
    Does not do authorization, which is handled in the admin page.
    """

    def __init__(self, email, firebaseID, admin=False, is_active=True):
        self.email = email
        self.firebaseID = firebaseID
        self.admin = admin
        self.is_active = True
        self.is_authenticated = True
        self.is_anonymous = False

    @staticmethod
    def from_dict(source):
        user = User(source['email'], source['firebaseID'])

        if 'admin' in source:
            user.admin = source['admin']

        if 'is_authenticated' in source:
            user.is_authenticated = source['is_authenticated']

        if 'is_active' in source:
            user.is_active = source['is_active']

        if 'is_anonymous' in source:
            user.is_anonymous = source['is_anonymous']

        return user

    @staticmethod
    def get(email=None, firebaseID=None):
        try:
            if email is not None:
                return User.from_dict(model_methods.get_user(email=email))
            elif firebaseID is not None:
                return User.from_dict(model_methods.get_user(firebaseID=firebaseID))
        except:
            return None


    def put(self):
        logging.info("Creating new user with email %s and firebaseID %s" % (str(self.email), str(self.firebaseID)))
        model_methods.put_user(self.to_dict())

    def get_id(self):
        return self.email


class Image(GenericModel):
    '''Represents an image, which has a URL and an album it belongs to.'''
       
    def __init__(self, url, album):
        self.url = url
        self.album = album

    @staticmethod
    def from_dict(source):
        image = Image(
            url=source['url'],
            album=source['album']
        )

        return image

    @staticmethod
    def get(url):
        try:
            return Image.from_dict(model_methods.get_image(url=url))
        except:
            return None

    def put(self):
        logging.info("Creating new image with url %s in album %s" % (str(self.url), str(self.album)))
        model_methods.put_image(self.to_dict())


class Album(GenericModel):
    '''Represents an album, which as a cover and set of images.'''

    def __init__(self, title, path, active=True, location=None, cover=None):
        self.title = title
        self.path = path
        self.active = active
        self.location = location
        self.cover = cover

    @staticmethod
    def from_dict(source):
        album = Album(
            title=source['title'],
            path=source['path'],
        )

        if 'active' in source:
            album.active = source['active']

        if 'location' in source:
            album.location = source['location']

        if 'cover' in source:
            album.cover = source['cover']

        return album

    @staticmethod
    def get(path):
        try:
            return Album.from_dict(model_methods.get_album(path=path))
        except:
            return None

    @staticmethod
    def active_albums(include_covers=False):
        albums_list = model_methods.get_active_albums()

        albums = []

        for album_dict in albums_list:
            album = Album.from_dict(album_dict)

            if not (album.title == cover_title and not include_covers):
                albums.append(album)

        return albums

    def put(self):
        logging.info("Creating new album with path %s" % str(self.path))
        model_methods.put_album(self.to_dict())
    
    def photos(self):
        ''' Return the photos belonging to this album'''
        images_list = model_methods.get_album_images(self.path)
        images = []

        for album_image_dict in images_list:
            album_image = Image.from_dict(album_image_dict)
            images.append(album_image)

        return images



    def update_cover(self, image_url):
        if Image.get(image_url) is None:
            raise Exception("Cover image must exist already before being assigned to an album as a cover")
        
        self.cover = image_url
        model_methods.update_cover(self.to_dict())


# run once
if Album.get(cover_title) is None:
    logging.info("Creating the covers album")
    cover_album = Album(cover_title, cover_title)
    cover_album.put()
