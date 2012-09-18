
from pyramid.security import has_permission
from pyramid.events import BeforeRender, subscriber


from webhelpers.paginate import PageURL_WebOb

from .resources import Root


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