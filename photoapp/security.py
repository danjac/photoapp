import binascii

from paste.httpheaders import AUTHORIZATION

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

def _get_credentials(request):
    """
    Get BASIC HTTP Auth creds for the API views.
    """

    auth = AUTHORIZATION(request.environ)

    try:
        method, auth = auth.split(' ', 1)
    except ValueError:
        return 

    if method.lower() == 'basic':

        try:
            auth = auth.strip().decode('base64')
        except binascii.Error:
            return

    try:
        email, password = auth.split(":", 1)
    except ValueError:
        return

    return (email, password)


class AuthenticationPolicy(AuthTktAuthenticationPolicy):

    def effective_principals(self, request):

        groups = [Everyone]

        if request.user and request.user.is_active:
            groups.append(Authenticated)
            groups.append(str(request.user.id))

            if request.user.is_admin:
                groups.append(Admins)

        return groups


def get_user(request):

    # if HTTP BASIC AUTH creds available, use those

    creds = _get_credentials(request)
    if creds:
        return User.authenticate(*creds)

    # otherwise check for user id in session

    user_id = unauthenticated_userid(request)

    if user_id:
        return DBSession.query(User).get(user_id)


def includeme(config):

    authn_policy = AuthenticationPolicy('seekret')
    authz_policy = ACLAuthorizationPolicy()

    config.set_root_factory(Root)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('view')

    config.set_request_property(get_user, 'user', reify=True)

