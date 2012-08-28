import unittest
import transaction

from pyramid import testing
from sqlalchemy import create_engine


class TestCase(unittest.TestCase):

    def setUp(self):
        testing.setUp()
        self.config = testing.setUp()
        engine = create_engine('sqlite://')
        from .models import (
            Base,
            )
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

        #with transaction.manager:
        #    model = MyModel(name='one', value=55)
        #     DBSession.add(model)

       
    def tearDown(self):
        DBSession.remove()
        testing.tearDown()


class HomeTests(TestCase):

    def test_home(self):

        from photoapp.views import home
        request = testing.DummyRequest()
        response = home(request)
        self.assert_('login_form' in response)


