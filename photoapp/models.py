import os
import hashlib
import urllib
import uuid
import base64
import mimetypes

import Image
import ImageOps

from cryptacular.bcrypt import BCRYPTPasswordManager
from pyramid.security import Allow

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
)


from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
)

from zope.sqlalchemy import ZopeTransactionExtension

from .utils import on_commit
from .security import Admins, UserID, PhotoID

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class Base(object):

    id = Column(Integer, primary_key=True)


class TimestampedMixin(object):

    @declared_attr
    def __ordering__(cls):
        return cls.created_at.desc()

    created_at = Column(DateTime, default=func.now())


Base = declarative_base(cls=Base)


_passwd_mgr = BCRYPTPasswordManager()


def includeme(config):

    engine = engine_from_config(config.get_settings(), 'sqlalchemy.')
    DBSession.configure(bind=engine)


def random_string():
    s = base64.urlsafe_b64encode(uuid.uuid4().bytes)
    for c in ('-', '_', '='):
        s = s.replace(c, '')
    return s


class User(TimestampedMixin, Base):

    __tablename__ = "users"

    email = Column(String(150), unique=True, nullable=False)
    first_name = Column(Unicode(40))
    last_name = Column(Unicode(40))

    _password = Column('password', String(80))

    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    last_login_at = Column(DateTime)

    key = Column(String(30), unique=True)

    photos = relationship("Photo",
                          innerjoin=True,
                          lazy="joined",
                          passive_deletes=True,
                          cascade="all,delete",
                          backref="owner")


    tags = relationship("Tag",
                        backref="owner",
                        cascade="all,delete",
                        passive_deletes=True)

    invites = relationship("Invite",
                           cascade="all,delete",
                           passive_deletes=True,
                           backref="sender")

    shared_photos = relationship("Photo",
                                 secondary="photos_users",
                                 backref="shared_users")

    def __unicode__(self):
        return self.name or self.email

    @classmethod
    def authenticate(cls, email, password):

        user = DBSession.query(cls).filter_by(
            email=email,
            is_active=True).first()

        if user and user.check_password(password):
            return user

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
        return self.key

    def gravatar_url(self, size):

        hashed = hashlib.md5(self.email.lower()).hexdigest()
        params = urllib.urlencode({'s': str(size)})

        return "http://www.gravatar.com/avatar/%s?%s" % (hashed, params)


class Photo(TimestampedMixin, Base):

    __tablename__ = "photos"

    owner_id = Column(Integer,
                      ForeignKey("users.id", ondelete="CASCADE"),
                      nullable=False,
                      index=True)

    title = Column(Unicode(100), index=True)
    image = Column(String(200), unique=True)

    height = Column(Integer)
    width = Column(Integer)

    tags = relationship("Tag",
                        secondary="photos_tags",
                        backref="photos")

    @property
    def content_type(self):
        return mimetypes.guess_type(self.image)[0]

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
            self.tags.append(Tag(name=name, owner=self.owner))

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
            (Allow, Admins, ("view", "edit", "delete")),

            (Allow, UserID(self.owner_id),
                ("view", "edit", "share", "delete")),

            (Allow, PhotoID(self.id),
                ("view", "copy", "delete_shared"))
        ]


class Invite(TimestampedMixin, Base):

    __tablename__ = "invites"

    accepted_on = Column(DateTime)

    email = Column(String(180), nullable=False)
    key = Column(String(30), unique=True, default=random_string)

    sender_id = Column(Integer,
                       ForeignKey("users.id", ondelete="CASCADE"),
                       nullable=False)

    photo_id = Column(Integer, ForeignKey("photos.id"))

    photo = relationship("Photo", backref="invites", cascade="delete")


class Tag(Base):

    __tablename__ = "tags"

    owner_id = Column(Integer,
                      ForeignKey("users.id", ondelete="CASCADE"),
                      nullable=False,
                      index=True)

    name = Column(String(100), nullable=False, index=True)

    frequency = Column(Integer, default=1)


    def __unicode__(self):
        return self.name or ''

    def __repr__(self):
        return "<%s>" % unicode(self)

    @property
    def __acl__(self):
        return [(Allow, UserID(self.owner_id), "view")]


photos_users = Table(
    "photos_users",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id"), primary_key=True),
)


photos_tags = Table(
    "photos_tags",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id"), primary_key=True),
)


# Events

def photo_tags_append_listener(target, value, initiator):
    """
    Increment tag frequency.
    """
    if value.frequency:
        value.frequency += 1
    else:
        value.frequency = 1

event.listen(Photo.tags, 'append', photo_tags_append_listener)


def photo_tags_remove_listener(target, value, initiator):
    """
    Decrement tag frequency. If freq == 0 then delete the tag.
    """
    value.frequency -= 1
    if value.frequency == 0:
        DBSession.delete(value)


event.listen(Photo.tags, 'remove', photo_tags_remove_listener)


def photo_delete_listener(mapper, connection, target):
    """
    Update tag frequency. If freq == 0 then delete the tag.
    """

    tags = Base.metadata.tables['tags']
    photos_tags = Base.metadata.tables['photos_tags']

    freq = select([func.count(photos_tags.c.tag_id)]).where(
        photos_tags.c.tag_id == tags.c.id
    )

    connection.execute(tags.update().values(frequency=freq))

    # remove any tags with frequency 0
    connection.execute(tags.delete().where(tags.c.frequency == 0))


event.listen(Photo, 'after_delete', photo_delete_listener)
