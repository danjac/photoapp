
from webassets import Bundle

bootstrap_css = Bundle(
    'bootstrap/css/*.css',
    filters='cssmin',
    output='bootstrap.css',
    debug=False,
)

bootstrap_js = Bundle(
    'bootstrap/js/*.js',
    filters='uglifyjs',
    output='bootstrap.js',
    debug=False,
)


jquery_js = Bundle(
    'jquery/*.js',
    filters='uglifyjs',
    output='jquery.js',
    debug=False,
)

def includeme(config):

    config.include('pyramid_webassets')

    config.add_webasset('bootstrap_css', bootstrap_css)
    config.add_webasset('bootstrap_js', bootstrap_js)
    #config.add_webasset('jquery_js', jquery_js)

    # Jinja2 integration
    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    jinja2_env = config.get_jinja2_environment()
    jinja2_env.assets_environment = config.get_webassets_env()


