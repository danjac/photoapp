import sys
import mailer

from pyramid.renderers import render

from .utils import with_transaction


def get_mailer(request):
    return Mailer.from_settings(request.registry.settings)

def includeme(config):
    config.set_request_property(get_mailer, 'mailer', reify=True)

        
class Mailer(mailer.Mailer):

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

    @with_transaction
    def send(self, msg):
        
        msg.From = msg.From or self.from_address

        if self.to_stdout:
            return self.send_to_stdout(msg)
        else:
            return super(Mailer, self).send(msg)


class Email(object):

    subject = None
    template = None
    html_template = None
    from_address = None
    cc = None
    bcc = None

    def __init__(self, request=None):
        self.request = request

    def get_recipients(self):
        return ()

    def get_cc(self):
        return self.cc
    
    def get_bcc(self):
        return self.bcc

    def get_body(self):
        if self.template:
            return render(self.template, self.get_context(), self.request)

    def get_html(self):
        if self.html_template:
            return render(self.html_template, self.get_context(), self.request)
        
    def get_subject(self):
        return self.subject

    def get_from_address(self):
        return self.from_address

    def get_context(self):
        return {}

    def get_attachments(self):
        return ()

    def _message(self):
        msg = mailer.Message(To=self.get_recipients(),
                             CC=self.get_cc(),
                             BCC=self.get_bcc(),
                             Subject=self.get_subject(),
                             From=self.get_from_address(),
                             Body=self.get_body(),
                             Html=self.get_html())

        for attachment in self.get_attachments():
            msg.attach(attachment)

        return msg

    def send(self, mailer=None):
        mailer = mailer or self.request.mailer
        mailer.send(self._message())


class ForgotPasswordEmail(Email):

    subject = "You forgot your password!"
    template = "emails/forgot_password.jinja2"

    def __init__(self, user, key, request=None):
        self.user = user
        self.key = key
        super(ForgotPasswordEmail, self).__init__(request)

    def get_recipients(self):
        return [self.user.email]

    def get_context(self):
        return {'user' : self.user, 'key' : self.key}


