import functools

from .resources import ModelResource
from .models import Photo, Tag

TagResource = ModelResource.for_model(Tag)
PhotoResource = ModelResource.for_model(Photo)

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

    config.add_route('tag', '/tag/{id}/{name}',
                     traverse='/{id}',
                     factory=TagResource)

    # auth routes

    config.add_route('login', '/login')
    config.add_route('signup', '/signup')
    config.add_route('forgot_pass', '/forgotpass')
    config.add_route('change_pass', '/changepass')
    config.add_route('logout', '/logout')

    # photo routes

    photo_route = functools.partial(config.add_route, 
                                    traverse='/{id}', 
                                    factory=PhotoResource)
    
    photo_route('thumbnail', '/thumbnail/{id}.jpg') 
    photo_route('image', '/photo/{id}.jpg') 
    photo_route('send', '/send/{id}') 
    photo_route('share', '/share/{id}') 
    photo_route('edit', '/edit/{id}') 
    photo_route('delete', '/delete/{id}')
    photo_route('copy', '/copy/{id}')
    photo_route('delete_shared', '/deleteshared/{id}')

     
