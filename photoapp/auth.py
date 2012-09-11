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
from .security import Admins, UserID, PhotoID


class AuthenticationPolicy(AuthTktAuthenticationPolicy):
    """
    Custom auth policy which permits both Basic Auth
    logins and session logins.
    """

    def get_basic_credentials(self, request):
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
            login, password = auth.split(":", 1)
        except ValueError:
            return

        return (login, password)

    def unauthenticated_userid(self, request):
        """
        Return an (login, password) tuple if
        Basic Auth, otherwise plain string or None.
        """

        userid = self.get_basic_credentials(request)

        if userid:
            return userid

        return super(AuthenticationPolicy,
                     self).unauthenticated_userid(request)

    def effective_principals(self, request):

        groups = [Everyone]

        if request.user and request.user.is_active:

            groups.append(Authenticated)
            groups.append(UserID(request.user.id))

            if request.user.is_admin:
                groups.append(Admins)

            for photo in request.user.shared_photos:
                groups.append(PhotoID(photo.id))

        return groups


def get_user(request):
    """
    Returns the current authenticated user
    """

    userid = unauthenticated_userid(request)

    if isinstance(userid, tuple):

        return User.authenticate(*userid)

    if userid:

        return DBSession.query(User).filter_by(
            is_active=True, id=userid
        ).first()


def includeme(config):

    authn_policy = AuthenticationPolicy('seekret')
    authz_policy = ACLAuthorizationPolicy()

    config.set_root_factory(Root)

    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_default_permission('view')

    config.set_request_property(get_user, 'user', reify=True)
