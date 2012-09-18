from pyramid.config import Configurator
from pyramid_beaker import set_cache_regions_from_settings


def main(global_config, **settings):
    #settings.setdefault('jinja2.i18n.domain', 'photoapp')

    config = Configurator(settings=settings)

    #config.add_translation_dirs('locale/')
    config.include('pyramid_jinja2')
    config.include('pyramid_beaker')
    config.include('pyramid_tm')
    config.include('pyramid_exclog')
    config.include('cornice')

    # my stuff
    config.include('photoapp.models')
    config.include('photoapp.storage')
    config.include('photoapp.auth')
    config.include('photoapp.mail')
    config.include('photoapp.assets')
    config.include('photoapp.routes')
    config.include('photoapp.tweens')

    # caching
    set_cache_regions_from_settings(settings)

    config.scan()

    return config.make_wsgi_app()
