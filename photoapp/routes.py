from .resources import ModelResource
from .models import Photo

def includeme(config):

    config.add_route('home', '/')
    config.add_route('upload', '/upload')

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('forgot_pass', '/forgot_pass')

    config.add_route('thumbnail', '/thumbnail/{id}.jpg', 
                     traverse='/{id}',
                     factory=ModelResource.for_model(Photo))
 
