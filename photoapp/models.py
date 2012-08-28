import os
import shutil
import uuid
import base64
import datetime

import Image
import ImageOps

import cryptacular.bcrypt

from cryptacular.bcrypt import BCRYPTPasswordManager
from pyramid.security import Allow, Authenticated

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Unicode,
    Boolean,
    DateTime,
    engine_from_config,
    func,
        )



from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()

_passwd_mgr = BCRYPTPasswordManager()


def get_storage(request):
    return FileStorage.from_settings(request.registry.settings)


def includeme(config):

    engine = engine_from_config(config.get_settings(), 'sqlalchemy.')
    DBSession.configure(bind=engine)

    config.set_request_property(get_storage, 'fs', reify=True)

    
class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    email = Column(String(150), unique=True, nullable=False)
    first_name = Column(Unicode(40))
    last_name = Column(Unicode(40))

    _password = Column('password', String(80))

    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now())
    last_login_at = Column(DateTime)

    def __unicode__(self):
        return self.name or self.email

    @property
    def name(self):
        if self.first_name and self.last_name:
            return self.first_name + " " + self.last_name

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def set_password(self, password):
        self._password = _passwd_mgr.encode(password)
    
    def check_password(self, password):
        return _passwd_mgr.check(self.password, password)


class Photo(Base):
    
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(Unicode(100))
    image = Column(String(200), unique=True)
    
    created_at = Column(DateTime, default=func.now())

    owner = relationship(User)

    @property
    def thumbnail(self):
        return "tn-" + self.image

    def load_thumbnail(self, fs):
        return fs.read(self.thumbnail)

    def save_image(self, fs, fp, name):
        """
        Save image to path
        """

        # create a GUID based name
        name, ext = os.path.splitext(name)

        base_name = base64.urlsafe_b64encode(uuid.uuid4().bytes)
        for c in ('-', '_', '='):
            base_name = base_name.replace(c, '')

        self.image = base_name + ext

        fs.copyfileobj(fp, self.image)

        img = Image.open(fs.path(self.image))
        img = ImageOps.fit(img, (300, 300), Image.ANTIALIAS)
        img.save(fs.path(self.thumbnail))

    
    @property
    def __acl__(self):
        return [
            (Allow, str(self.owner_id), "view"),
        ]


class FileStorage(object):

    @classmethod
    def from_settings(cls, settings):
        return cls(settings['photoapp.uploads_dir'])

    def path(self, name):
        return os.path.join(self.base_dir, name)

    def read(self, name):
        return open(self.path(name), "rb").read()

    def copyfileobj(self, fp, name):
        shutil.copyfileobj(fp, open(self.path(name), "wb"))

    def __init__(self, base_dir):
        self.base_dir = base_dir




