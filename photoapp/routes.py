import functools

from .resources import ModelResource
from .models import Photo, Tag, User

TagResource = ModelResource.for_model(Tag)
PhotoResource = ModelResource.for_model(Photo)
UserResource = ModelResource.for_model(User)


def includeme(config):

    config.add_route('welcome', '/')
    config.add_route('home', '/home')
    config.add_route('about', '/about')
    config.add_route('contact', '/contact')
    config.add_route('settings', '/settings')
    config.add_route('upload', '/upload')
    config.add_route('search', '/search')
    config.add_route('tags', '/tags')
    config.add_route('shared', '/shared')
    config.add_route('my_shared', '/my_shared')
    config.add_route('public_all', '/all')

    config.add_route('public', '/user/{id:\d+}',
                     traverse='/{id}',
                     factory=UserResource)

    config.add_route('tag', '/tag/{id:\d+}/{name}',
                     traverse='/{id}',
                     factory=TagResource)

    # auth routes

    config.add_route('signup', '/signup')
    config.add_route('delete_account', '/delete_account'),

    # photo routes

    photo_route = functools.partial(config.add_route,
                                    traverse='/{id}',
                                    factory=PhotoResource)

    photo_route('thumbnail', '/thumbnail/{id:\d+}.jpg')
    photo_route('image', '/photo/{id:\d+}.jpg')
    photo_route('download', '/download/{id:\d+}.jpg')
    photo_route('share', '/share/{id:\d+}')
    photo_route('edit', '/edit/{id:\d+}')
    photo_route('delete', '/delete/{id:\d+}')
    photo_route('copy', '/copy/{id:\d+}')
    photo_route('delete_shared', '/deleteshared/{id:\d+}')
