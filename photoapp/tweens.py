from pyramid.security import unauthenticated_userid
from beaker import cache


def includeme(config):
    config.add_tween('photoapp.tweens.cache_anonymous')


def cache_anonymous(handler, registry):
    """
    Tween which returns a cached response if:

    1) it's HTTP GET
    2) there is no logged in user

    The cache key should be the request url.
    """

    def _tween(request):

        # pre - 1.4: no access to custom request properties

        user_id = unauthenticated_userid(request)

        @cache.cache_region('default', request.path_url)
        def _cached_response():
            response = handler(request)
            if response is not None:
                return handler(request)

        if not request.params and user_id is None:
            return _cached_response()

        return handler(request)

    return _tween
