import functools

from .resources import ModelResource
from .models import Photo

def includeme(config):

    config.add_route('home', '/')
    config.add_route('upload', '/upload')

    # auth routes

    config.add_route('login', '/login')
    config.add_route('forgot_pass', '/forgot_pass')
    config.add_route('change_pass', '/change_pass')
    config.add_route('logout', '/logout')

    # photo routes

    photo_route = functools.partial(config.add_route, 
                                    traverse='/{id}', 
                                    factory=ModelResource.for_model(Photo))
    
    photo_route('thumbnail', '/thumbnail/{id}.jpg') 
    photo_route('image', '/photo/{id}.jpg') 
    photo_route('send', '/send/{id}') 

