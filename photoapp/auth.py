from pyramid.security import (
    unauthenticated_userid,
    Everyone,
    Authenticated,
)

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .resources import Root
from .models import User, DBSession
from .security import Admins, Verified, UserID, PhotoID


class AuthenticationPolicy(AuthTktAuthenticationPolicy):
    def effective_principals(self, request):

        groups = [Everyone]

        if request.user and request.user.is_active:

            groups.append(Authenticated)
            groups.append(UserID(request.user.id))

            if request.user.is_complete:
                groups.append(Verified)

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
