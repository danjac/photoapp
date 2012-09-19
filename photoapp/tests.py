import os
import cgi
import shutil
import mock
import unittest
import datetime

import transaction

from pyramid import testing
from pyramid.paster import get_appsettings
from pyramid.security import Allow, Everyone
from pyramid.authorization import ACLAuthorizationPolicy

#from webtest import TestApp
#from webtest.debugapp import debug_app

from wtforms.validators import ValidationError

from sqlalchemy import engine_from_config

from webob.multidict import MultiDict


class MockRoute(object):
    """Fakes out a route_url call."""
    def __init__(self, route_name, **params):

        self.route_name = route_name
        self.params = params


class TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        root_dir = os.path.dirname(os.path.dirname(__file__))
        config_ini = os.path.join(root_dir, 'test.ini')
        cls.settings = get_appsettings(config_ini)
        cls.engine = engine_from_config(cls.settings, 'sqlalchemy.')

    def setUp(self):

        from .models import DBSession, Base

        self.config = testing.setUp(settings=self.settings)
        self.dbconn = self.engine.connect()
        self.trans = self.dbconn.begin()

        DBSession.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)

        try:
            os.makedirs("test_uploads")
        except OSError:
            pass

    def get_app(self):
        from . import main
        return main(self.config, **self.settings)

    def make_POST_request(self, **data):

        request = testing.DummyRequest()
        request.method = "POST"
        request.session = mock.Mock()
        data.setdefault('csrf_token', request.session.get_csrf_token())
        request.POST = MultiDict(data)
        request.params.update(request.POST)
        request.route_url = MockRoute
        return request

    def tearDown(self):
        from .models import DBSession

        self.trans.rollback()

        shutil.rmtree("test_uploads")

        DBSession.remove()
        testing.tearDown()


class ConfiguratorTests(TestCase):

    def test_main(self):
        """
        Test load whole app
        """

        from . import main
        self.assert_(main(self.config, **self.settings))


class StorageTests(TestCase):

    def test_path(self):

        from .storage import FileStorage

        settings = self.config.get_settings()

        path = os.path.join(settings['photoapp.filestorage.base_dir'],
                            'test.jpg')

        fs = FileStorage.from_settings(settings)
        self.assert_(fs.path("test.jpg") == path)

    def test_file_obj(self):

        from .storage import FileStorage

        fs = FileStorage.from_settings(self.config.get_settings())
        fo = fs.file("test.jpg")
        self.assert_(fo.path == fs.path("test.jpg"))

    def test_file_obj_delete_if_not_exists(self):

        from .storage import FileStorage

        fs = FileStorage("test_uploads")
        fo = fs.file("test.jpg")
        self.assert_(not fo.exists())
        fo.delete()
        self.assert_(not fo.exists())

    def test_file_obj_delete(self):

        from .storage import FileStorage

        shutil.copyfile(os.path.join("test_media", "coffee.jpg"),
                        os.path.join("test_uploads", "test.jpg"))

        fs = FileStorage("test_uploads")
        fo = fs.file("test.jpg")
        self.assert_(fo.exists())
        fo.delete()
        self.assert_(not fo.exists())

    def test_file_obj_copy(self):

        from .storage import FileStorage

        fs = FileStorage("test_uploads")
        fp = open(os.path.join("test_media", "coffee.jpg"))
        fo = fs.file("test.jpg")
        self.assert_(not fo.exists())
        fo.copy(fp)
        self.assert_(fo.exists())

    def test_file_obj_exists_if_does_exist(self):

        from .storage import FileStorage

        fs = FileStorage("test_media")
        fo = fs.file("coffee.jpg")
        self.assert_(fo.exists())

    def test_file_obj_exists_if_does_not_exist(self):

        from .storage import FileStorage

        fs = FileStorage("test_media")
        fo = fs.file("foo.jpg")
        self.assert_(not fo.exists())

    def test_file_storage_read(self):
        from .storage import FileStorage

        fs = FileStorage("test_media")
        self.assert_(fs.read("coffee.jpg"))

    def test_file_obj_read(self):
        from .storage import FileStorage

        fs = FileStorage("test_media")
        fo = fs.file("coffee.jpg")
        self.assert_(fo.read())

    def test_file_obj_write(self):
        from .storage import FileStorage

        fs = FileStorage("test_uploads")
        fo = fs.file("test.txt")
        fo.write("testing")

        self.assert_(fo.exists())
        self.assert_(fo.read() == "testing")


class PhotoTests(TestCase):

    def test_delete_with_tags(self):

        from .models import User, Photo, DBSession, Tag

        user = User(email="tester@gmail.com")
        DBSession.add(user)
        DBSession.flush()

        photo = Photo(owner=user, owner_id=user.id)
        photo.taglist = "landscapes norway winter snow"

        DBSession.add(photo)
        DBSession.flush()

        self.assert_(len(photo.tags) == 4)

        DBSession.delete(photo)

        self.assert_(DBSession.query(Tag).count() == 0)

    def test_add_tags_if_none(self):

        from .models import User, Photo

        user = User(email="tester@gmail.com")
        photo = Photo(owner=user)
        photo.taglist = None

        self.assert_(photo.tags == [])

    def test_add_tags_if_all_new(self):

        from .models import User, Photo

        user = User(email="tester@gmail.com")
        photo = Photo(owner=user)
        photo.taglist = "landscapes norway winter snow"

        self.assert_(len(photo.tags) == 4)
        tag = photo.tags[0]
        self.assert_(tag.frequency == 1)

    def test_add_tags_if_dupes(self):

        from .models import User, Photo

        user = User(email="tester@gmail.com")
        photo = Photo(owner=user)
        photo.taglist = "landscapes norway snow winter snow"

        self.assert_(len(photo.tags) == 4)

    def test_add_tags_if_exist(self):

        from .models import User, Photo, DBSession

        user = User(email="tester@gmail.com")
        DBSession.add(user)
        DBSession.flush()

        photo = Photo(owner=user)
        DBSession.add(photo)

        photo.taglist = "landscapes norway winter snow"

        DBSession.flush()

        self.assert_(len(photo.tags) == 4)

        photo = Photo(owner=user)
        photo.taglist = "norway winter snow skiing"

        self.assert_(len(photo.tags) == 4)

    def test_save_image(self):

        from .storage import FileStorage
        from .models import Photo

        fs = FileStorage("test_uploads")
        fp = open(os.path.join("test_media", "coffee.jpg"), "rb")

        photo = Photo()
        photo.save_image(fs, fp, "test.jpg")

        self.assert_(photo.get_image(fs).exists())
        self.assert_(photo.get_thumbnail(fs).exists())
        self.assert_(photo.image != "test.jpg")
        self.assert_(photo.image.endswith(".jpg"))

        self.assert_(photo.height)
        self.assert_(photo.width)

    def test_acl(self):

        from .security import Admins
        from .models import Photo

        photo = Photo(id=1, owner_id=1)

        acl = [
            (Allow, Admins, ("view", "edit", "delete")),
            (Allow, "user:1", ("view", "edit", "share", "delete")),
            (Allow, "photo:1", ("view", "copy", "delete_shared")),
        ]

        self.assert_(photo.__acl__ == acl)

    def test_acl_if_public(self):

        from .security import Admins
        from .models import Photo

        photo = Photo(id=1, owner_id=1, is_public=True)

        acl = [
            (Allow, Admins, ("view", "edit", "delete")),
            (Allow, "user:1", ("view", "edit", "share", "delete")),
            (Allow, "photo:1", ("view", "copy", "delete_shared")),
            (Allow, Everyone, "view"),
        ]

        self.assert_(photo.__acl__ == acl)


class UserTests(TestCase):

    def test_reset_key(self):

        from .models import User
        u = User()
        self.assert_(u.reset_key() is not None)

    def test_set_password(self):

        from .models import User
        u = User(password="test")
        self.assert_(u.password != "test")

    def test_check_password_good(self):

        from .models import User
        u = User(password="test")
        self.assert_(u.check_password("test"))

    def test_check_password_bad(self):

        from .models import User
        u = User(password="test")
        self.assert_(not u.check_password("TEST"))

    def test_authenticate_if_no_user(self):

        from .models import User

        u = User.authenticate("tester@gmail.com", "test")
        self.assert_(u is None)

    def test_authenticate_if_bad_email(self):

        from .models import User, DBSession

        u = User(email="tester@gmail.com", password="test")
        DBSession.add(u)
        DBSession.flush()

        u = User.authenticate("TESTER@gmail.com", "test")
        self.assert_(u is None)

    def test_authenticate_if_bad_password(self):

        from .models import User, DBSession

        u = User(email="tester@gmail.com", password="test")
        DBSession.add(u)
        DBSession.flush()

        u = User.authenticate("tester@gmail.com", "test1")
        self.assert_(u is None)

    def test_authenticate_if_inactive(self):

        from .models import User, DBSession

        u = User(email="tester@gmail.com", password="test", is_active=False)
        DBSession.add(u)
        DBSession.flush()

        u = User.authenticate("tester@gmail.com", "test")
        self.assert_(u is None)

    def test_authenticate_if_all_ok(self):

        from .models import User, DBSession

        u = User(email="tester@gmail.com", password="test")
        DBSession.add(u)
        DBSession.flush()

        u = User.authenticate("tester@gmail.com", "test")
        self.assert_(u is not None)


class SignupTests(TestCase):

    def test_get_signup_without_invite(self):
        """
        Email should be blank.
        """

        from .views import signup

        res = signup(testing.DummyRequest())
        self.assert_(res['form'].email.data is None)

    def test_get_signup_with_invite(self):
        """
        We should have email == invite email.
        """

        from .models import User, Photo, Invite, DBSession
        from .views import signup

        user = User(email="tester@gmail.com")
        photo = Photo(title="test", image="test.jpg", owner=user)
        invite = Invite(email="friend@gmail.com", sender=user, photo=photo)

        DBSession.add_all((user, photo, invite))
        DBSession.flush()

        req = testing.DummyRequest()
        req.params['invite'] = invite.key

        res = signup(req)
        self.assert_(res['form'].email.data == 'friend@gmail.com')

    def test_post_signup_without_invite(self):

        from .views import signup
        from .models import User, DBSession

        req = self.make_POST_request(
            email="tester@gmail.com",
            password="test",
            password_again="test",
            first_name="Tester",
            last_name="Tester",
        )

        req.user = None

        res = signup(req)

        self.assert_(res.status_int == 302)
        self.assert_(res.location.route_name == 'home')
        self.assert_(DBSession.query(User).count() == 1)

    def test_post_signup_with_accepted_invite(self):

        from .views import signup
        from .models import User, Photo, Invite, DBSession

        user = User(email="tester@gmail.com")
        photo = Photo(title="test", image="test.jpg", owner=user)
        invite = Invite(email="friend@gmail.com",
                        sender=user,
                        accepted_on=datetime.datetime.now(),
                        photo=photo)

        DBSession.add_all((user, photo, invite))
        DBSession.flush()

        req = self.make_POST_request(
            email="friend@gmail.com",
            password="test",
            password_again="test",
            first_name="Tester",
            last_name="Tester",
            invite=invite.key
        )

        req.user = None

        res = signup(req)

        self.assert_(res.status_int == 302)
        self.assert_(res.location.route_name == 'home')
        self.assert_(DBSession.query(User).count() == 2)
        self.assert_(invite.accepted_on is not None)

    def test_post_signup_with_invite(self):

        from .views import signup
        from .models import User, Photo, Invite, DBSession

        user = User(email="tester@gmail.com")
        photo = Photo(title="test", image="test.jpg", owner=user)
        invite = Invite(email="friend@gmail.com", sender=user, photo=photo)

        DBSession.add_all((user, photo, invite))
        DBSession.flush()

        req = self.make_POST_request(
            email="friend@gmail.com",
            password="test",
            password_again="test",
            first_name="Tester",
            last_name="Tester",
            invite=invite.key
        )

        req.user = None

        res = signup(req)

        self.assert_(res.status_int == 302)
        self.assert_(res.location.route_name == 'shared')
        self.assert_(DBSession.query(User).count() == 2)
        self.assert_(invite.accepted_on is not None)


class HomeTests(TestCase):

    def test_home_if_logged_in_user(self):

        from .views import home
        from .models import User, Photo, DBSession

        user = User(email="danjac354@gmail.com")
        photo = Photo(owner=user, title="test", image="test.jpg")

        DBSession.add_all([user, photo])
        DBSession.flush()

        request = testing.DummyRequest()
        request.user = user

        response = home(request)
        self.assert_(len(response['page'].items) == 1)

        self.assert_('login_form' not in response)


class LoginTests(TestCase):

    def setUp(self):
        super(LoginTests, self).setUp()

    def test_login_valid_user(self):

        from .views import login
        from .models import User, DBSession

        u = User(email="danjac354@gmail.com", password="test")
        DBSession.add(u)
        DBSession.flush()

        request = self.make_POST_request(
            email="danjac354@gmail.com",
            password="test",
        )

        request.host = "example.com"
        request.matched_route = mock.Mock()
        request.matched_route.name = "home"

        response = login(request)
        self.assert_(response.status_code == 302)
        self.assert_(response.location.route_name == "home")

    def test_login_invalid_user(self):

        from .views import login

        request = self.make_POST_request(
            email="danjac354@gmail.com",
            password="test"
        )

        request.matched_route = mock.Mock()
        request.matched_route.name = "home"

        response = login(request)
        self.assert_('form' in response)

    def test_login_to_other_domain(self):
        """
        If current page is "login" we should redirect
        to the home page instead.
        """

        from .views import login
        from .models import User, DBSession

        u = User(email="danjac354@gmail.com", password="test")
        DBSession.add(u)
        DBSession.flush()

        redirect = "http://google.com"

        request = self.make_POST_request(
            email="danjac354@gmail.com",
            next=redirect,
            password="test"
        )

        request.host = "example.com"
        request.matched_route = mock.Mock()
        request.matched_route.name = "login"
        request.url = redirect

        response = login(request)
        form = response['form']
        self.assert_(form.errors['next'] == ['Invalid domain'])

    def test_login_to_login_page(self):
        """
        If current page is "login" we should redirect
        to the home page instead.
        """

        from .views import login
        from .models import User, DBSession

        u = User(email="danjac354@gmail.com", password="test")
        DBSession.add(u)
        DBSession.flush()

        redirect = "http://example.com/login"

        request = self.make_POST_request(
            email="danjac354@gmail.com",
            next=redirect,
            password="test"
        )

        request.host = "example.com"
        request.matched_route = mock.Mock()
        request.matched_route.name = "login"
        request.url = redirect

        response = login(request)
        self.assert_(response.status_code == 302)
        self.assert_(response.location.route_name == "home")

    def test_login_to_another_page(self):

        from .views import login
        from .models import User, DBSession

        u = User(email="danjac354@gmail.com", password="test")
        DBSession.add(u)
        DBSession.flush()

        redirect = "http://example.com/upload"

        request = self.make_POST_request(
            email="danjac354@gmail.com",
            next=redirect,
            password="test"
        )

        request.host = "example.com"
        request.matched_route = mock.Mock()
        request.matched_route.name = "upload"
        request.url = redirect

        response = login(request)
        self.assert_(response.status_code == 302)
        self.assert_(response.location == "http://example.com/upload")


class WelcomeTests(TestCase):

    def test_welcome_if_no_user(self):

        from .views import welcome

        req = testing.DummyRequest()
        req.user = None
        res = welcome(req)
        photos = res['photos']
        self.assert_(len(list(photos)) == 0)

    def test_welcome_if_user(self):

        from .views import welcome
        from .models import User

        req = testing.DummyRequest()
        req.user = User()
        req.route_url = MockRoute
        res = welcome(req)
        self.assert_(res.status_int == 302)
        self.assert_(res.location.route_name == 'home')


class ForgotPasswordTests(TestCase):

    def test_if_user_found(self):

        from .models import User, DBSession
        from .views import forgot_password
        from .mail import DummyMailer

        user = User(email="tester@gmail.com", password="test")

        DBSession.add(user)
        DBSession.flush()

        req = self.make_POST_request(email="tester@gmail.com")
        req.mailer = DummyMailer()

        res = forgot_password(req)
        self.assert_(res.status_int == 302)
        self.assert_(len(req.mailer.messages), 1)


class ImageRequiredTests(TestCase):

    def test_with_non_image(self):

        from .forms import ImageRequired

        form = mock.Mock()
        field = mock.Mock()
        field.data = "test"

        self.assertRaises(ValidationError, ImageRequired(), form, field)

    def test_with_non_image_file(self):

        from .forms import ImageRequired

        form = mock.Mock()
        field = mock.Mock()

        fs = cgi.FieldStorage()
        fs.filename = "test.txt"
        field.data = fs

        self.assertRaises(ValidationError, ImageRequired(), form, field)

    def test_with_png(self):

        from .forms import ImageRequired

        form = mock.Mock()
        field = mock.Mock()

        fs = cgi.FieldStorage()
        fs.filename = "test.png"
        field.data = fs

        ImageRequired()(form, field)

    def test_with_jpeg(self):

        from .forms import ImageRequired

        form = mock.Mock()
        field = mock.Mock()

        fs = cgi.FieldStorage()
        fs.filename = "test.jpg"
        field.data = fs

        ImageRequired()(form, field)


class SharedPhotosTests(TestCase):

    def test_shared_photos(self):

        from .models import User, Photo, DBSession
        from .views import shared_photos

        user = User(email="danjac354@gmail.com")
        photo = Photo(owner=user, title="test", image="test.jpg")
        user2 = User(email="user2@gmail.com")
        user2.shared_photos.append(photo)

        DBSession.add_all([user, photo, user2])

        req = testing.DummyRequest()
        req.user = user2

        res = shared_photos(req)
        self.assert_(res['page'].item_count == 1)


class SignupFormTests(TestCase):

    def test_signup_with_unused_email(self):

        from .forms import SignupForm

        req = self.make_POST_request(
            email="tester@gmail.com",
            first_name="Dan",
            last_name="Tester",
            password="test",
            password_again="test"
        )

        req.user = None

        form = SignupForm(req)
        self.assert_(form.validate())

    def test_signup_with_used_email(self):

        from .forms import SignupForm
        from .models import User, DBSession

        user = User(email="tester@gmail.com", password="test")

        DBSession.add(user)
        DBSession.flush()

        req = self.make_POST_request(
            email="tester@gmail.com",
            first_name="Dan", last_name="Tester",
            password="test",
            password_again="test"
        )

        req.user = None

        form = SignupForm(req)
        self.assert_(not form.validate())


class PublicPhotoTests(TestCase):

    def test_public_photos(self):

        from .models import User, Photo, DBSession
        from .views import public_photos_for_user

        user = User(email="tester@gmail.com", password="test")
        photo = Photo(title="test", owner=user, is_public=True)

        DBSession.add_all((user, photo))
        DBSession.flush()

        res = public_photos_for_user(user, testing.DummyRequest())
        self.assert_(res['page'].item_count == 1)


class AccountFormTests(TestCase):

    def test_with_same_user_email(self):

        from .forms import AccountForm
        from .models import User, DBSession

        user = User(email="tester@gmail.com", password="test")

        DBSession.add(user)
        DBSession.flush()

        req = self.make_POST_request(
            email="tester@gmail.com",
            first_name="Dan",
            last_name="Tester",
            password="test",
            password_again="test"
        )

        req.user = user

        form = AccountForm(req)
        self.assert_(form.validate())

    def test_with_another_user_email(self):

        from .forms import AccountForm
        from .models import User, DBSession

        user = User(email="tester@gmail.com", password="test")

        DBSession.add(user)
        DBSession.flush()

        user2 = User(email="tester2@gmail.com", password="test")

        DBSession.add(user2)
        DBSession.flush()

        req = self.make_POST_request(
            email="tester2@gmail.com",
            first_name="Dan",
            last_name="Tester",
            password="test",
            password_again="test"
        )

        req.user = user

        form = AccountForm(req)
        self.assert_(not form.validate())


class EmailTests(TestCase):

    def test_send_shared_photo_email(self):

        from .models import User, Photo
        from .views import send_shared_photo_email
        from .storage import FileStorage
        from .mail import DummyMailer

        request = testing.DummyRequest()
        request.mailer = DummyMailer()
        request.route_url = mock.Mock()

        request.user = User(first_name="Dan",
                            last_name="Jacob",)

        request.fs = FileStorage("test_media")
        note = "testing"

        photo = Photo(owner=request.user, title="test", image="test.jpg")

        note = "testing"

        recipient = User(email="tester@gmail.com",
                         first_name="Tester")

        send_shared_photo_email(request, photo, recipient, note)

        msg = request.mailer.messages[0]
        self.assert_(msg.To == recipient.email)
        self.assert_(note in msg.Body)

    def test_send_invite_email(self):

        from .models import User, Invite, Photo
        from .views import send_invite_email
        from .storage import FileStorage
        from .mail import DummyMailer

        request = testing.DummyRequest()
        request.mailer = DummyMailer()
        request.route_url = mock.Mock()

        request.user = User(first_name="Dan",
                            last_name="Jacob",)

        request.fs = FileStorage("test_media")
        note = "testing"

        photo = Photo(owner=request.user, image="test.jpg")

        invite = Invite(sender=request.user,
                        photo=photo,
                        email="tester@gmail.com")

        send_invite_email(request, invite, note)

        msg = request.mailer.messages[0]
        self.assert_(msg.To == invite.email)
        self.assert_(note in msg.Body)


class AuthenticationTests(TestCase):

    def test_get_user_if_none(self):

        from .auth import get_user

        self.config.set_authorization_policy(ACLAuthorizationPolicy())

        authn_policy = testing.DummySecurityPolicy()
        self.config.set_authentication_policy(authn_policy)

        request = testing.DummyRequest()
        request.user = None
        request.environ['wsgi.version'] = '1.0'

        self.assert_(get_user(request) is None)

    def test_get_user_if_invalid(self):

        from .auth import get_user

        self.config.set_authorization_policy(ACLAuthorizationPolicy())

        authn_policy = testing.DummySecurityPolicy(userid="1")
        self.config.set_authentication_policy(authn_policy)

        request = testing.DummyRequest()
        request.user = None
        request.environ['wsgi.version'] = '1.0'

        self.assert_(get_user(request) is None)

    def test_get_user_if_valid(self):

        from .auth import get_user
        from .models import User, DBSession

        with transaction.manager:

            user = User(email="danjac354@gmail.com")
            DBSession.add(user)
            DBSession.flush()

            self.config.set_authorization_policy(ACLAuthorizationPolicy())

            authn_policy = testing.DummySecurityPolicy(userid=str(user.id))
            self.config.set_authentication_policy(authn_policy)

            request = testing.DummyRequest()
            request.user = None
            request.environ['wsgi.version'] = '1.0'

            self.assert_(get_user(request) == user)

            DBSession.delete(user)


class SearchTests(TestCase):

    def make_photo(self):

        from .models import User, Photo, DBSession

        user = User(email="tester@gmail.com")
        photo = Photo(title="Lamborghini", owner=user, image="test.jpg")
        photo.taglist = "wallpaper cars"

        DBSession.add_all((user, photo))
        DBSession.flush()

        return photo

    def test_search_with_no_items(self):

        from .views import search

        req = testing.DummyRequest()
        res = search(req)
        self.assert_(res['page'].item_count == 0)

    def test_search_by_title(self):

        from .views import search

        photo = self.make_photo()

        req = testing.DummyRequest()
        req.user = photo.owner
        req.GET['search'] = 'lamborghini'
        res = search(req)

        self.assert_(res['page'].item_count == 1)
        self.assert_(res['page'].items[0] == photo)

    def test_search_if_one_good_one_bad(self):

        from .views import search

        photo = self.make_photo()

        req = testing.DummyRequest()
        req.user = photo.owner
        req.GET['search'] = 'lamborghini ferrari'
        res = search(req)

        self.assert_(res['page'].item_count == 0)

    def test_search_by_keyword(self):

        from .views import search

        photo = self.make_photo()

        req = testing.DummyRequest()
        req.user = photo.owner
        req.GET['search'] = 'wallpaper'
        res = search(req)

        self.assert_(res['page'].item_count == 1)
        self.assert_(res['page'].items[0] == photo)

    def test_search_if_other_user(self):

        from .views import search
        from .models import User, DBSession

        self.make_photo()

        other = User(email="another@gmail.com")
        DBSession.add(other)
        DBSession.flush()

        req = testing.DummyRequest()
        req.user = other
        req.GET['search'] = 'lamborghini'
        res = search(req)

        self.assert_(res['page'].item_count == 0)


class TestGetTags(TestCase):

    def test_get_tags(self):

        from .models import User, Tag, DBSession
        from .views import get_tags

        user = User(email="tester@gmail.com")
        tag = Tag(name='wallpaper', owner=user, frequency=1)

        DBSession.add_all((user, tag))
        DBSession.flush()

        req = testing.DummyRequest()
        req.user = user
        req.route_url = MockRoute

        res = get_tags(req)

        self.assert_(res['tags'][0]['text'] == 'wallpaper')
        self.assert_(res['tags'][0]['weight'] == 1)
        self.assert_(res['tags'][0]['link'].route_name == 'tag')
        self.assert_(res['tags'][0]['link'].params['id'] == tag.id)
        self.assert_(res['tags'][0]['link'].params['name'] == 'wallpaper')


class ChangePasswordTests(TestCase):

    def test_if_no_key_found(self):

        from pyramid.httpexceptions import HTTPForbidden

        from .views import change_password

        self.assertRaises(HTTPForbidden,
                          change_password,
                          testing.DummyRequest())

    def test_if_no_user_found(self):

        from pyramid.httpexceptions import HTTPForbidden

        from .views import change_password

        req = testing.DummyRequest()
        req.params['key'] = 'foo'

        self.assertRaises(HTTPForbidden, change_password, req)

    def test_if_user_found(self):

        from .views import change_password
        from .models import User, DBSession

        user = User(email="tester@gmail.com", key="foo")
        DBSession.add(user)
        DBSession.flush()

        req = testing.DummyRequest()
        req.params['key'] = 'foo'

        res = change_password(req)
        self.assert_(res['form'] is not None)
        self.assert_(res['form'].key.data == 'foo')

    def test_change_password_successfully(self):

        from .views import change_password
        from .models import User, DBSession

        user = User(email="tester@gmail.com", key="foo", password="test1")
        self.assert_(user.check_password('test1'))

        DBSession.add(user)
        DBSession.flush()

        req = self.make_POST_request(password='test2',
                                     password_again='test2',
                                     key='foo')

        req.user = user
        res = change_password(req)
        self.assert_(res.location.route_name == 'login')

        self.assert_(user.check_password('test2'))
