
import os
import sys

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
)

from ..models import Base


def main(argv=sys.argv):
    """
    Drops test database. You should  have a test.ini
    config file setup with correct sqlalchemy settings
    to the test DB.
    """

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    config_ini = os.path.join(root_dir, 'test.ini')

    settings = get_appsettings(config_ini)
    engine = engine_from_config(settings, 'sqlalchemy.')
    Base.metadata.drop_all(engine)
