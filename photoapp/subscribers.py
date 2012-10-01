
from pyramid.security import has_permission
from pyramid.events import BeforeRender, subscriber

from webhelpers.paginate import PageURL_WebOb

from .resources import Root
from .forms import LoginForm


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
