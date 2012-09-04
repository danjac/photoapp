import os
import uuid
import base64
import datetime
import logging

import Image
import ImageOps

import cryptacular.bcrypt

from cryptacular.bcrypt import BCRYPTPasswordManager
from pyramid.security import Allow, Authenticated

from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    String,
    Unicode,
    Boolean,
    DateTime,
    engine_from_config,
    func,
    event,
    select,
    and_,
        )


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from .utils import on_commit

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

Base = declarative_base()

_passwd_mgr = BCRYPTPasswordManager()


def includeme(config):

    engine = engine_from_config(config.get_settings(), 'sqlalchemy.')
    DBSession.configure(bind=engine)

def random_string():
    s = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    for c in ('-', '_', '='):
        s = s.replace(c, '')
    return s 

    
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

    key = Column(String(30), unique=True)

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

    def reset_key(self):
        self.key = random_string()


class Photo(Base):
    
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(Unicode(100))
    image = Column(String(200), unique=True)

    height = Column(Integer)
    width = Column(Integer)

    created_at = Column(DateTime, default=func.now())

    owner = relationship("User")

    tags = relationship("Tag", 
                        secondary="photos_tags", 
                        backref="photos")

    @property
    def taglist(self):
        return " ".join([t.name for t in self.tags])

    @taglist.setter
    def taglist(self, taglist):

        taglist = (taglist or '').strip().lower().split()
        taglist = set(name for name in taglist if name)

        ignore = set()

        # remove any unused tags

        for tag in self.tags:
            if tag.name in taglist:
                ignore.add(tag.name)
            else:
                self.tags.remove(tag)

        # find existing tags

        taglist = taglist - ignore

        ignore = set()

        for tag in self.owner.tags:
            if tag.name in taglist:
                self.tags.append(tag)
                ignore.add(tag.name)

        taglist = taglist - ignore

        for name in taglist:
            self.tags.append(Tag(name=name, owner_id=self.owner_id))


    @property
    def thumbnail(self):
        return "tn-" + self.image

    def get_thumbnail(self, fs):
        return fs.file(self.thumbnail)

    def get_image(self, fs):
        return fs.file(self.image)

    def save_image(self, fs, fp, name):

        # create a GUID based name
        name, ext = os.path.splitext(name)

        base_name = random_string()

        self.image = base_name + ext

        image_obj = self.get_image(fs)
        image_obj.copy(fp)

        img = Image.open(image_obj.path)

        self.width, self.height = img.size

        img = ImageOps.fit(img, (300, 300), Image.ANTIALIAS)
        img.save(self.get_thumbnail(fs).path)

    save_image_on_commit = on_commit(save_image)

    def delete_image(self, fs):

        self.get_image(fs).delete()
        self.get_thumbnail(fs).delete()

    delete_image_on_commit = on_commit(delete_image)
   
    @property
    def __acl__(self):
        return [
            (Allow, str(self.owner_id), ("view", "edit", "delete")),
        ]


class Tag(Base):

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100))
    frequency = Column(Integer, default=1)

    owner = relationship("User", backref="tags")

    def __unicode__(self):
        return self.name or ''

    def __repr__(self):
        return "<%s>" % unicode(self)

    @property
    def __acl__(self):
        return [(Allow, str(self.owner_id), "view")]


photos_tags = Table(
    "photos_tags", 
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id"), primary_key=True),
)


# Events

def photo_tags_append_listener(target, value, initiator):
    if value.frequency:
        value.frequency += 1
    else:
        value.frequency = 1

event.listen(Photo.tags, 'append', photo_tags_append_listener)


def photo_tags_remove_listener(target, value, initiator):
    value.frequency -= 1
    if value.frequency == 0:
        DBSession.delete(value)


event.listen(Photo.tags, 'remove', photo_tags_remove_listener)


def photo_delete_listener(mapper, connection, target):

    tags = Base.metadata.tables['tags']
    photos_tags = Base.metadata.tables['photos_tags']

    freq = select([func.count(photos_tags.c.tag_id)]).where(
        photos_tags.c.tag_id==tags.c.id
        )

    u = tags.update().values(frequency=freq)

    connection.execute(u)

    # remove any tags with frequency 0

    d = tags.delete().where(tags.c.frequency==0)
    connection.execute(d)


event.listen(Photo, 'after_delete', photo_delete_listener)

