import os
import mock
import unittest
import transaction

from pyramid import testing
from pyramid.paster import get_appsettings
#from sqlalchemy import create_engine
from sqlalchemy import engine_from_config
from webob.multidict import MultiDict



class TestCase(unittest.TestCase):

    def setUp(self):

        from .models import DBSession, Base

        root_dir = os.path.dirname(os.path.dirname(__file__))
        config_ini = os.path.join(root_dir, 'test.ini')
        
        settings = get_appsettings(config_ini)

        self.config = testing.setUp(settings=settings)
        self.engine = engine_from_config(settings, 'sqlalchemy.')
        self.dbconn = self.engine.connect()
        self.trans = self.dbconn.begin()

        DBSession.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)

       
    def tearDown(self):
        from .models import DBSession, Base

        self.trans.rollback()

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


class PhotoTests(TestCase):

    def test_add_tags_if_none(self):

        from .models import User, Photo, DBSession, Tag

        user = User(email="tester@gmail.com")
        photo = Photo(owner=user)
        tags  = photo.add_tags(None)

        self.assert_(tags == [])
        self.assert_(DBSession.query(Tag).count() == 0)

    def test_add_tags_if_all_new(self):

        from .models import User, Photo, DBSession, Tag

        user = User(email="tester@gmail.com")
        photo = Photo(owner=user)
        tags = photo.add_tags("landscapes norway winter snow")

        self.assert_(len(tags) == 4)
        self.assert_(DBSession.query(Tag).count() == 4)

    def test_add_tags_if_dupes(self):

        from .models import User, Photo, DBSession, Tag

        user = User(email="tester@gmail.com")
        photo = Photo(owner=user)
        tags = photo.add_tags("landscapes norway snow winter snow")

        self.assert_(len(tags) == 4)
        self.assert_(DBSession.query(Tag).count() == 4)

    def test_add_tags_if_exist(self):

        from .models import User, Photo, DBSession, Tag

        user = User(email="tester@gmail.com")
        DBSession.add(user)

        photo = Photo(owner=user)
        DBSession.add(photo)

        tags = photo.add_tags("landscapes norway winter snow")

        DBSession.flush()

        self.assert_(len(tags) == 4)
        self.assert_(DBSession.query(Tag).count() == 4)

        photo = Photo(owner=user)
        tags = photo.add_tags("norway winter snow skiing")

        self.assert_(len(tags) == 4)
        self.assert_(len(photo.tags) == 4)
        self.assert_(DBSession.query(Tag).count() == 5)

        for tag in tags:
            if tag.name in ("norway", "winter", "snow"):
                self.assert_(tag.frequency == 2)
            else:
                self.assert_(tag.frequency == 1)



class UserTests(TestCase):

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


class HomeTests(TestCase):

    def test_home_if_anonymous(self):
        from .views import home

        request = testing.DummyRequest()
        request.user = None

        response = home(request)
        self.assert_('photos' not in response)
        self.assert_('login_form' in response)

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

    def get_POST_req(self, **data):

        request = testing.DummyRequest()
        request.method = "POST"
        request.session = mock.Mock()
        data.setdefault('csrf_token', request.session.get_csrf_token())
        request.POST = MultiDict(data)
        return request

    def test_login_valid_user(self):

        from .views import login
        from .models import User, DBSession

        # add this so we can redirect
        self.config.include('photoapp.routes')

        u = User(email="danjac354@gmail.com", password="test")
        DBSession.add(u)
        DBSession.flush()
        
        request = self.get_POST_req(email="danjac354@gmail.com",
                                    password="test")

        response = login(request)
        self.assert_(response.status_code == 302)
        self.assert_(response.location == "http://example.com/")

    def test_login_invalid_user(self):

        from .views import login

        request = self.get_POST_req(email="danjac354@gmail.com",
                                    password="test")

        response = login(request)
        self.assert_('form' in response)
 
