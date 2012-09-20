
import os
import sys
import transaction

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid_webassets import get_webassets_env_from_settings

from ..assets import assets

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)

    config_uri = argv[1]

    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    env = get_webassets_env_from_settings(settings)

    for name, bundle in assets:
        print("Building asset {0}".format(name))
        bundle.build(env)
