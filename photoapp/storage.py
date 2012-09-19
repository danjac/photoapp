import os
import shutil
import logging

from zope.interface import Attribute, Interface, implementer


def get_storage(request):
    return request.registry.queryUtility(IFileStorage)


def includeme(config):

    config.registry.registerUtility(
        FileStorage.from_settings(config.get_settings()), IFileStorage)

    config.set_request_property(get_storage, 'fs', reify=True)


class IFileStorage(Interface):

    def from_settings(settings, prefix):
        """Create IFileStorage instance from settings.

        Args:
            settings: dict of settings
            prefix: prefix used to find storage-specific settings

        Returns:
            IFileStorage instance
        """

    def path(name):
        """Returns absolute full path to given name

        Args:
            name: relative filename
        Returns:
            Absolute path to name
        """

    def file(name):
        """Returns IFileObj instance

        Args:
            name: relative filename
        Returns:
            IFileObj instance
        """

    def read(name):
        """Reads contents of file

        Args:
            name: relative filename
        Returns:
            file contents
        """


class IFileObj(Interface):
    """
    Refers to a specific file.
    """

    path = Attribute("Path to given file")

    def open(mode):
        """Returns a file pointer to the

        Args:
            mode: file mode e.g. "wb"
        Returns:
            pointer to file
        """

    def read():
        """Opens file

        Returns:
            file contents
        """

    def write(contents):
        """Writes string to file storage

        Args:
            contents: string to write
        """

    def copy(fp):
        """Copies file to location

        Args:
            fp: file pointer
        """

    def delete():
        """Deletes file"""

    def exists():
        """Checks if file exists

        Returns:
            boolean
        """


@implementer(IFileObj)
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


@implementer(IFileStorage)
class FileStorage(object):

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
