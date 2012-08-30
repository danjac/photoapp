import mailer
import transaction

from pyramid.renderers import render


def get_mailer(request):
    return Mailer.from_settings(request.registry.settings)

def includeme(config):
    config.set_request_property(get_mailer, 'mailer', reify=True)

        
class MailDataManager(object):
    """
    Handle emails inside transaction
    """
    transaction_manager = transaction.manager

    def __init__(self, callable, *args, **kwargs):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs

    def commit(self):
        pass

    def abort(self, transaction):
        pass

    def tpc_begin(self):
        pass
    
    def tpc_vote(self):
        pass

    def tpc_finish(self, transaction):
        self.callable(*self.args, **self.kwargs)

    tpc_abort = abort


class Mailer(mailer.Mailer):

    @classmethod
    def from_settings(cls, settings):
        
        defaults = (
            ('host', 'localhost'),
            ('port', 0),
            ('use_tls', false),
            ('usr', None),
            ('pwd', None),
            ('use_ssl', false)
            )

        kw = {}

        for name, default in defaults:
            kw[name] = settings.get('photoapp.mailer.%s' % name, default)
        
        return cls(**kw)

    def __init__(self, *args, **kwargs):
        self.from_address = kwargs.pop('from_address', None)
        super(Mailer, self).__init__(*args, **kwargs)

    def send(self, msg):
        
        msg.From = msg.From or self.from_address
        transaction.get().join(super(Mailer, self).send, msg)


class Email(object):

    subject = None
    template = None
    html_template = None
    from_address = None
    recipient = None
    cc = None
    bcc = None

    def __init__(self, request=None):
        self.request = request

    def get_recipient(self):
        return self.recipient

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
        msg = Message(To=self.get_recipient(),
                      CC=self.get_cc(),
                      BCC=self.get_bcc(),
                      From=self.get_from_address(),
                      Body=self.get_body(),
                      Html=self.get_html())

        for attachment in self.get_attachments():
            msg.attach(attachment)

    def send(self, mailer=None):
        mailer = mailer or self.request.mailer
        mailer.send(self._message())
