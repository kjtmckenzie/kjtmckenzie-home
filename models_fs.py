import logging
import six
import base64
import model_methods

cover_title = "covers"

class GenericModel(object):

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




# how do we prevent duplicate users from being created?
class User(GenericModel):
    def __init__(self, email, admin=False):
        self.email = email
        self.admin = admin

    @staticmethod
    def from_dict(source):
        user = User(source['email'])

        if 'admin' in source:
            user.admin = source['admin']

        return user

    @staticmethod
    def get(email):
        try:
            return User.from_dict(model_methods.get_user(email=email))
        except:
            return None


    def put(self):
        model_methods.put_user(self.to_dict())


class Image(GenericModel):
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
        model_methods.put_image(self.to_dict())


class Album(GenericModel):
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
        model_methods.put_album(self.to_dict())

    def set_cover(self, image_url):
        if Image.get(image_url) is None:
            raise Exception("Cover image must exist already before being assigned to an album as a cover")
        
        self.cover = image_url


# run once
if Album.get(cover_title) is None:
    print("Creating the covers album")
    cover_album = Album(cover_title, cover_title)
    cover_album.put()
