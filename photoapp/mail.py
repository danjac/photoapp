import sys
import mailer


from .utils import on_commit


def get_mailer(request):
    return Mailer.from_settings(request.registry.settings)

def includeme(config):
    config.set_request_property(get_mailer, 'mailer', reify=True)

        
class Mailer(mailer.Mailer):
    """
    Modified Mailer class:

    1. Runs inside transaction, so unwanted emails don't get sent

    2. from_settings classmethod loads config settings

    3. to_stdout option prints email to console for dev/testing
       instead of sending

    4. from_address option gives site-wide default From address
    """

    @classmethod
    def from_settings(cls, settings):
        
        defaults = (
            ('host', 'localhost'),
            ('port', 0),
            ('use_tls', False),
            ('usr', None),
            ('pwd', None),
            ('from_address', None),
            ('to_stdout', False),
            #('use_ssl', False)
            )

        kw = {}

        for name, default in defaults:
            kw[name] = settings.get('photoapp.mailer.%s' % name, default)
        
        return cls(**kw)

    def __init__(self, *args, **kwargs):
        self.to_stdout = kwargs.pop('to_stdout', False)
        self.from_address = kwargs.pop('from_address', None)
        super(Mailer, self).__init__(*args, **kwargs)

    def send_to_stdout(self, msg):
        sys.stdout.write(msg.as_string())

    @on_commit
    def send(self, msg):
        
        msg.From = msg.From or self.from_address

        if self.to_stdout:
            return self.send_to_stdout(msg)
        else:
            return super(Mailer, self).send(msg)


