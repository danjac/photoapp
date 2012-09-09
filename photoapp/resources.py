from pyramid.security import Allow, Authenticated
from pyramid.exceptions import NotFound

from .models import DBSession


class Root(object):

    def __init__(self, request):
        self.__acl__ = [
            (Allow, Authenticated, "view"),
            (Allow, Authenticated, "upload"),
        ]
        self.__name__ = "root"
        self.__parent__ = None


class ModelResource(object):

    model = None

    @classmethod
    def for_model(cls, model):
        def _resource(request):
            return cls(request, model)
        return _resource

    def __init__(self, request, model=None):
        self.request = request
        self.model = model or self.model

    def __getitem__(self, key):
        obj = self.get_object(key)
        if obj is None:
            raise NotFound()

        obj.__name___ = key
        return obj

    def get_object(self, id):
        return DBSession.query(self.model).get(id)
