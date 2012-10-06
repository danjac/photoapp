from pyramid.security import (
    authenticated_userid,
    Everyone,
    Authenticated,
)

from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from .resources import Root
from .models import User, DBSession
from .security import Admins, UserID, PhotoID


class AuthenticationPolicy(SessionAuthenticationPolicy):
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

    email = authenticated_userid(request)

    if email:

        return DBSession.query(User).filter_by(
            is_active=True, email=email
        ).first()


def includeme(config):

    authn_policy = AuthenticationPolicy()

    config.set_root_factory(Root)

    config.set_authentication_policy(authn_policy)
    config.set_default_permission('view')

    config.set_request_property(get_user, 'user', reify=True)
