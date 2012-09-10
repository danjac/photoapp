import os
import cgi
import shutil
import mock
import unittest

from pyramid import testing
from pyramid.paster import get_appsettings
from pyramid.security import Allow

#from webtest import TestApp
#from webtest.debugapp import debug_app

from wtforms.validators import ValidationError

from sqlalchemy import engine_from_config

from webob.multidict import MultiDict


class DummyMailer(object):
    """
    Mock mailer object. Saves message instances
    instead of sending them.
    """

    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)


class TestCase(unittest.TestCase):

    def setUp(self):

        from .models import DBSession, Base

        root_dir = os.path.dirname(os.path.dirname(__file__))
        config_ini = os.path.join(root_dir, 'test.ini')

        self.settings = get_appsettings(config_ini)
        self.config = testing.setUp(settings=self.settings)
        self.engine = engine_from_config(self.settings, 'sqlalchemy.')
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

    def load_routes(self):
        # add this so we can redirect
        self.config.include('photoapp.routes')

    def get_POST_req(self, **data):

        request = testing.DummyRequest()
        request.method = "POST"
        request.session = mock.Mock()
        data.setdefault('csrf_token', request.session.get_csrf_token())
        request.POST = MultiDict(data)
        return request

    def tearDown(self):
        from .models import DBSession

        self.trans.rollback()

        shutil.rmtree("test_uploads")

        DBSession.remove()
        testing.tearDown()


class StorageTests(TestCase):

    def test_path(self):

        from .storage import FileStorage

        settings = self.config.get_settings()
        path = os.path.join(settings['photoapp.uploads_dir'], 'test.jpg')

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
            (Allow, "shared:1", ("view", "copy", "delete_shared")),
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

        request = self.get_POST_req(email="danjac354@gmail.com",
                                    password="test")

        request.matched_route = mock.Mock()
        request.matched_route.name = "home"

        self.load_routes()

        response = login(request)
        self.assert_(response.status_code == 302)
        self.assert_(response.location == "http://example.com/home")

    def test_login_invalid_user(self):

        from .views import login

        request = self.get_POST_req(email="danjac354@gmail.com",
                                    password="test")

        request.matched_route = mock.Mock()
        request.matched_route.name = "home"

        response = login(request)
        self.assert_('form' in response)

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

        request = self.get_POST_req(email="danjac354@gmail.com",
                                    next=redirect,
                                    password="test")

        request.matched_route = mock.Mock()
        request.matched_route.name = "login"
        request.url = redirect

        self.load_routes()

        response = login(request)
        self.assert_(response.status_code == 302)
        self.assert_(response.location == "http://example.com/home")

    def test_login_to_another_page(self):

        from .views import login
        from .models import User, DBSession

        u = User(email="danjac354@gmail.com", password="test")
        DBSession.add(u)
        DBSession.flush()

        redirect = "http://example.com/upload"

        request = self.get_POST_req(email="danjac354@gmail.com",
                                    next=redirect,
                                    password="test")

        request.matched_route = mock.Mock()
        request.matched_route.name = "upload"
        request.url = redirect

        self.load_routes()

        response = login(request)
        self.assert_(response.status_code == 302)
        self.assert_(response.location == "http://example.com/upload")


class WelcomeTests(TestCase):

    def test_welcome_if_no_user(self):

        from .views import welcome

        req = testing.DummyRequest()
        req.user = None
        res = welcome(req)
        self.assert_(res == {})

    def test_welcome_if_user(self):

        from .views import welcome
        from .models import User

        self.load_routes()

        req = testing.DummyRequest()
        req.user = User()
        res = welcome(req)
        self.assert_(res.status_int == 302)
        self.assert_(res.location == 'http://example.com/home')


class ForgotPasswordTests(TestCase):

    def test_if_user_found(self):

        from .models import User, DBSession
        from .views import forgot_password

        user = User(email="tester@gmail.com", password="test")

        DBSession.add(user)
        DBSession.flush()

        req = self.get_POST_req(email="tester@gmail.com")
        req.mailer = DummyMailer()

        self.load_routes()

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


class SignupFormTests(TestCase):

    def test_signup_with_unused_email(self):

        from .forms import SignupForm

        req = self.get_POST_req(email="tester@gmail.com",
                                first_name="Dan",
                                last_name="Tester",
                                password="test",
                                password_again="test")

        form = SignupForm(req)
        self.assert_(form.validate())

    def test_signup_with_used_email(self):

        from .forms import SignupForm
        from .models import User, DBSession

        user = User(email="tester@gmail.com", password="test")

        DBSession.add(user)
        DBSession.flush()

        req = self.get_POST_req(email="tester@gmail.com",
                                first_name="Dan",
                                last_name="Tester",
                                password="test",
                                password_again="test")

        form = SignupForm(req)
        self.assert_(not form.validate())


class EditAccountFormTests(TestCase):

    def test_with_no_obj_passed(self):

        from .forms import EditAccountForm
        self.assertRaises(ValueError, EditAccountForm, testing.DummyRequest())

    def test_with_same_user_email(self):

        from .forms import EditAccountForm
        from .models import User, DBSession

        user = User(email="tester@gmail.com", password="test")

        DBSession.add(user)
        DBSession.flush()

        req = self.get_POST_req(email="tester@gmail.com",
                                first_name="Dan",
                                last_name="Tester",
                                password="test",
                                password_again="test")

        form = EditAccountForm(req, obj=user)
        self.assert_(form.validate())

    def test_with_another_user_email(self):

        from .forms import EditAccountForm
        from .models import User, DBSession

        user = User(email="tester@gmail.com", password="test")

        DBSession.add(user)
        DBSession.flush()

        user2 = User(email="tester2@gmail.com", password="test")

        DBSession.add(user2)
        DBSession.flush()

        req = self.get_POST_req(email="tester2@gmail.com",
                                first_name="Dan",
                                last_name="Tester",
                                password="test",
                                password_again="test")

        form = EditAccountForm(req, obj=user)
        self.assert_(not form.validate())
