from pyramid.security import (
    unauthenticated_userid, 
    Everyone, 
    Authenticated,
)

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .resources import Root
from .models import User, DBSession

Admins = "system:Admins"

def groupfinder(userid, request):
    groups = [Everyone]

    if request.user and request.user.is_active:
        groups.append(Authenticated)
        groups.append(userid)

        if request.user.is_admin:
            groups.append(Admins)

    return groups


def get_user(request):

    user_id = unauthenticated_userid(request)

    if user_id:
        return DBSession.query(User).get(user_id)


def includeme(config):

    authn_policy = AuthTktAuthenticationPolicy('seekret', callback=groupfinder)
    authz_policy = ACLAuthorizationPolicy()

    config.set_root_factory(Root)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('view')

    config.set_request_property(get_user, 'user', reify=True)

