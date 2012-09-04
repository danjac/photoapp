import os
import shutil
import logging


def get_storage(request):
    return FileStorage.from_settings(request.registry.settings)


def includeme(config):
    config.set_request_property(get_storage, 'fs', reify=True)


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
        self.open("rb").write(contents)

    def copy(self, fp):
        shutil.copyfileobj(fp, self.open("wb"))
        
    def delete(self):
        try:
            os.remove(self.path)
        except OSError, e:
            logging.exception(e)


class FileStorage(object):

    @classmethod
    def from_settings(cls, settings):
        return cls(settings['photoapp.uploads_dir'])

    def path(self, name):
        return os.path.join(self.base_dir, name)

    def file(self, name):
        return FileObj(self, name)

    def read(self, name):
        return self.file(name).read()

    def __init__(self, base_dir):
        self.base_dir = base_dir


