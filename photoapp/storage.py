import os
import shutil
import logging

from zope.interface import Interface, implements


def get_storage(request):
    return request.registry.queryUtility(IFileStorage)


def includeme(config):

    config.registry.registerUtility(
        FileStorage.from_settings(config.get_settings()), IFileStorage)

    config.set_request_property(get_storage, 'fs', reify=True)


class IFileStorage(Interface):

    def from_settings(settings, prefix):
        pass

    def path(name):
        pass

    def file(name):
        pass

    def read(name):
        pass


class FileObj(object):

    def __init__(self, fs, name):
        self.fs = fs
        self.name = name
        self.path = self.fs.path(self.name)

    def open(self, mode):
        return open(self.path, mode)

    def read(self):
        return self.open("rb").read()

    def write(self, contents):
        self.open("wb").write(contents)

    def copy(self, fp):
        shutil.copyfileobj(fp, self.open("wb"))

    def delete(self):
        try:
            os.remove(self.path)
        except OSError, e:
            logging.exception(e)

    def exists(self):
        return os.path.exists(self.path)


class FileStorage(object):

    implements(IFileStorage)

    @classmethod
    def from_settings(cls, settings, prefix='photoapp.filestorage.'):
        return cls(settings[prefix + 'base_dir'])

    def path(self, name):
        return os.path.join(self.base_dir, name)

    def file(self, name):
        return FileObj(self, name)

    def read(self, name):
        return self.file(name).read()

    def __init__(self, base_dir):
        self.base_dir = base_dir
