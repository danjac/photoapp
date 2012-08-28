import datetime
import cryptacular.bcrypt

from cryptacular.bcrypt import BCRYPTPasswordManager
from pyramid.security import Allow, Authenticated

from mongoengine import (
    Document,
    StringField,
    EmailField,
    BooleanField,
    DateTimeField,
    ImageField,
    ListField,
    ReferenceField,

)

from mongoengine.queryset import QuerySet


_passwd_mgr = BCRYPTPasswordManager()


class UserQuerySet(QuerySet):

    def authenticate(self, email, password):

        user = self.filter(is_active=True, email=email).first()
        if user and user.check_password(password):
            return user


class User(Document):

    email = EmailField(unique=True)
    first_name = StringField()
    last_name = StringField()

    password = StringField()
    is_active = BooleanField(default=True)
    is_admin = BooleanField(default=False)

    created_at = DateTimeField(default=datetime.datetime.now)
    last_login_at = DateTimeField()

    meta = {'queryset_class' : UserQuerySet}

    def __unicode__(self):
        return self.name or self.email

    @property
    def name(self):
        if self.first_name and self.last_name:
            return self.first_name + " " + self.last_name

    def set_password(self, password):
        self.password = _passwd_mgr.encode(password)
    
    def check_password(self, password):
        return _passwd_mgr.check(self.password, password)


class Photo(Document):

    owner = ReferenceField(User)
    title = StringField()
    image = ImageField(thumbnail_size=(300, 300, True))
    tags = ListField(StringField)

    created_at = DateTimeField(default=datetime.datetime.now)

    @property
    def __acl__(self):
        return [
            (Allow, str(self.owner.id), "view"),
        ]

