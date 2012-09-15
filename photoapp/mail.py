import sys
import mailer

from zope.interface import Interface, implements

from .manager import on_commit


def get_mailer(request):
    return request.registry.queryUtility(IMailer)


def includeme(config):

    config.registry.registerUtility(
        mailer_settings_factory(config.get_settings()), IMailer)

    config.set_request_property(get_mailer, 'mailer', reify=True)


class IMailer(Interface):

    def from_settings(settings, prefix):
        pass

    def send(msg):
        pass


def mailer_settings_factory(settings, prefix='photoapp.mailer.'):

    mailer_type = settings.get(prefix + 'type', 'console')
    mailer_cls = _mailer_classes[mailer_type]
    return mailer_cls.from_settings(settings, prefix)


class SMTP_Mailer(mailer.Mailer):

    implements(IMailer)

    @classmethod
    def from_settings(cls, settings, prefix='photoapp.mailer.'):

        defaults = (
            ('host', 'localhost'),
            ('port', 0),
            ('use_tls', False),
            ('usr', None),
            ('pwd', None),
            ('from_address', None),
            #('use_ssl', False)
        )

        kw = {}

        for name, default in defaults:
            kw[name] = settings.get(prefix + name, default)

        return cls(**kw)

    def __init__(self, *args, **kwargs):
        self.from_address = kwargs.pop('from_address', None)
        super(SMTP_Mailer, self).__init__(*args, **kwargs)

    @on_commit
    def send(self, msg):

        msg.From = msg.From or self.from_address
        super(SMTP_Mailer, self).send(msg)


class ConsoleMailer(object):
    """
    Just dumps message to stdout. Use for development/testing.
    """

    implements(IMailer)

    @classmethod
    def from_settings(cls, settings, prefix='photoapp.mailer.'):
        return cls(from_address=settings.get(prefix + 'from_address'))

    def __init__(self, from_address=None):
        self.from_address = from_address

    @on_commit
    def send(self, msg):
        sys.stdout.write(msg.as_string())


_mailer_classes = {
    'smtp': SMTP_Mailer,
    'console': ConsoleMailer,
}
