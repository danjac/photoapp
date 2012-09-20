
from pyramid.security import has_permission
from pyramid.events import BeforeRender, NewRequest, subscriber
from pyramid.httpexceptions import HTTPForbidden


from webhelpers.paginate import PageURL_WebOb

from .resources import Root
from .forms import LoginForm


@subscriber(NewRequest)
def verify_csrf_token(event):
    """In POST requests, check that the CSRF
    token is included with the requests.

    Note that in most cases using forms this
    check is redundant as the form itself
    should validate CSRF. Nonetheless not all
    POST requests will use forms.

    The request POST should include a `csrf_token`
    value as generated by request.session.get_csrf_token().
    """

    request = event.request
    if request.method == "POST":

        csrf_token = request.POST.get('csrf_token')
        if not csrf_token or csrf_token != request.session.get_csrf_token():
            raise HTTPForbidden()


@subscriber(BeforeRender)
def add_renderer_globals(event):
    """
    Add template global functions here
    """

    request = event['request']
    root = Root(request)

    def _has_permission(permission, context=None):
        """
        Check for permission (root context by default)
        """
        context = context or root
        return has_permission(permission, context, request)

    event['has_permission'] = _has_permission
    event['page_url'] = PageURL_WebOb(request)
    event['login_form'] = LoginForm(request)

    event['google_tracking_code'] = request.registry.settings.get(
        'photoapp.google_tracking_code'
    )
