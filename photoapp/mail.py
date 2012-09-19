import sys
import mailer

from zope.interface import Interface, implementer

from .manager import on_commit


def get_mailer(request):
    """Custom request property: adds IMailer instance to
    current request.
    """

    return request.registry.queryUtility(IMailer)


def includeme(config):
    """Pyramid configuration hook:

    Registers IMailer instance and adds to current request
    as `mailer` property.
    """

    config.registry.registerUtility(
        mailer_settings_factory(config.get_settings()), IMailer)

    config.set_request_property(get_mailer, 'mailer', reify=True)


def mailer_settings_factory(settings, prefix='photoapp.mailer.'):
    """Returns the correctly configured specific implementation
    of an IMailer object based on settings.

    The specific implementation is determined by the `type`
    setting, currently:

    smtp:
        send mail from SMTP server
    console:
        print mail messages to stdout (does not send any mail)

    `console` is the default type.

    Args:
        settings: dict of settings
        prefix: specific prefix to find mailer-specific settings

    Returns:
        IMailer instance
    """

    mailer_type = settings.get(prefix + 'type', 'console')
    mailer_cls = _mailer_classes[mailer_type]
    return mailer_cls.from_settings(settings, prefix)


class IMailer(Interface):
    """Abstracts mail sending functionality.
    """

    def from_settings(settings, prefix):
        """Create instance of IMailer object from settings

        Args:
            settings: dict of settings
            prefix: specific prefix to find mailer-specific settings

        Returns:
            IMailer instance.
        """

    def send(msg):
        """Sends a mail message according underlying implementation.

        Args:
            msg: mailer.Message instance
        """


@implementer(IMailer)
class SMTP_Mailer(mailer.Mailer):
    """Sends email message through SMTP. The following specific settings are
    required:

        host: host (default `localhost`)
        port: port number (default 0)
        use_tls: TLS-enabled (default False)
        usr: username
        pwd: password
        from_address: default "from" address used if none provided
    """

    @classmethod
    def from_settings(cls, settings, prefix):

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


@implementer(IMailer)
class ConsoleMailer(object):
    """Just dumps message to stdout. Use for development/testing.
    """

    @classmethod
    def from_settings(cls, settings, prefix):
        return cls(from_address=settings.get(prefix + 'from_address'))

    def __init__(self, from_address=None):
        self.from_address = from_address

    @on_commit
    def send(self, msg):
        sys.stdout.write(msg.as_string())


@implementer(IMailer)
class DummyMailer(object):
    """Mock mailer object. Saves message instances
    as property `messages` instead of sending them, so
    message contents etc can be tests.
    """

    @classmethod
    def from_settings(cls, settings, prefix):
        return cls(from_address="support@example.com")

    def __init__(self, from_address=None):
        self.messages = []
        self.from_address = from_address

    def send(self, message):
        self.messages.append(message)


_mailer_classes = {
    'smtp': SMTP_Mailer,
    'console': ConsoleMailer,
    'dummy': DummyMailer,
}
