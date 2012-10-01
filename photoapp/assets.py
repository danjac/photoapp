
from webassets import Bundle

assets = (

    (
        'bootstrap_css', Bundle(
            'bootstrap/css/bootstrap.css',
            'bootstrap/css/bootstrap-responsive.css',
            filters='cssmin',
            output='css/bootstrap.css',
            debug=False,
        )

    ),

    (
        'bootstrap_js', Bundle(
            'bootstrap/js/*.js',
            filters='uglifyjs',
            output='js/bootstrap.js',
            debug=False,
        )
    ),


    (
        'jquery_js', Bundle(
            'jquery/jquery-1.8.0.min.js',
            'jquery/jqcloud-1.0.1.min.js',
            'jquery/underscore-min.js',
            filters='uglifyjs',
            output='js/jquery.js',
            debug=False,
        )
    ),

    (
        'jquery_css', Bundle(
            'jquery/*.css',
            filters='cssmin',
            output='css/jquery.css',
            debug=False,
        )
    ),

    (
        'ias_js', Bundle(
            'ias/*.js',
            filters='uglifyjs',
            output='js/ias.js',
            debug=False,
        )
    ),

    (
        'ias_css', Bundle(
            'ias/*.css',
            filters='cssmin',
            output='css/ias.css',
            debug=False,
        )
    ),


    (
        'photoapp_js', Bundle(
            'photoapp/coffee/*.coffee',
            filters='coffeescript,uglifyjs',
            output='js/photoapp.js',
            debug=False,
        )
    ),
)


def includeme(config):

    config.include('pyramid_webassets')

    for name, bundle in assets:
        config.add_webasset(name, bundle)

    # jinja2 integration
    config.add_jinja2_extension('webassets.ext.jinja2.AssetsExtension')
    jinja2_env = config.get_jinja2_environment()
    jinja2_env.assets_environment = config.get_webassets_env()

    # add static views
    config.add_static_view('static', 'static')
