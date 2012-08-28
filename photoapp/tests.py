import unittest

from mongoengine import connection 
from pyramid import testing


class TestCase(unittest.TestCase):

    db_name = "test_photoapp"

    def setUp(self):
        connection.connect(self.db_name)
        testing.setUp()
        
    def tearDown(self):

        connection.get_connection().drop_database(self.db_name)
        connection.disconnect()

        testing.tearDown()


class HomeTests(TestCase):

    def test_home(self):

        from photoapp.views import home
        request = testing.DummyRequest()
        response = home(request)
        self.assert_('login_form' in response)


class UserTests(TestCase):

    def test_authenticate_if_no_user(self):

        from photoapp.models import User

        user = User.objects.authenticate("tester@gmail.com", "test")
        self.assert_(user is None)

    def test_authenticate_if_user_ok(self):

        from photoapp.models import User

        user = User(email="tester@gmail.com")
        user.set_password("test")
        user.save()

        user = User.objects.authenticate("tester@gmail.com", "test")
        self.assert_(user is not None)

    def test_authenticate_if_user_inactive(self):

        from photoapp.models import User

        user = User(email="tester@gmail.com", is_active=False)
        user.set_password("test")
        user.save()

        user = User.objects.authenticate("tester@gmail.com", "test")
        self.assert_(user is None)

    def test_authenticate_if_wrong_email(self):

        from photoapp.models import User

        user = User(email="tester@gmail.com")
        user.set_password("test")
        user.save()

        user = User.objects.authenticate("tester2@gmail.com", "test")
        self.assert_(user is None)

    def test_authenticate_if_wrong_password(self):

        from photoapp.models import User

        user = User(email="tester@gmail.com")
        user.set_password("test")
        user.save()

        user = User.objects.authenticate("tester@gmail.com", "test2")
        self.assert_(user is None)





