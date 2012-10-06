
from pyramid.security import has_permission
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.events import BeforeRender, NewRequest, subscriber

from webhelpers.paginate import PageURL_WebOb
from webhelpers.html import tags

from .resources import Root
from .forms import LoginForm


@subscriber(NewRequest)
def check_csrf(event):
    """Checks CSRF with each POST request"""
    if event.request.method == "POST":
        # add this in 1.4a2:
        #event.request.session.check_csrf()
        if event.request.POST.get(
                'csrf_token') != event.request.session.get_csrf_token():
            raise HTTPBadRequest('Invalid CSRF token')


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
    event['login_form'] = LoginForm()
    event['h'] = tags


    event['google_tracking_code'] = request.registry.settings.get(
        'photoapp.google_tracking_code'
    )
