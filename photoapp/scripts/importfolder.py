import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import DBSession, Base, User, Photo
from ..storage import FileStorage

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <email> <folder>\n'
          '(example %s development.ini danjac354@gmail.com ~/wallpaper' % (
                  cmd, cmd))

    sys.exit(1)


def add_new_photos(owner, fs, dir):

    for (path, dirs, files) in os.walk(dir):
        for filename in files:
            if filename.endswith(".jpg"):

                name, ext = os.path.splitext(filename)
                rel_path = path[len(dir):]
                tags = rel_path.replace(os.path.sep, " ")

                full_path = os.path.join(path, filename)
                print(full_path)

                photo = Photo(owner=owner, title=name)

                try:
                    photo.save_image(fs, open(full_path, "rb"), filename)
                except IOError:
                    print("%s is not an image" % full_path)
                    continue

                DBSession.add(photo)
                photo.add_tags(tags)


    

def main(argv=sys.argv):

    if len(argv) != 4:
        usage(argv)

    config_uri = argv[1]
    email = argv[2]
    base_dir = argv[3]

    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    storage = FileStorage.from_settings(settings)

    user = DBSession.query(User).filter_by(email=email).first()

    if user is None:
        print("No user found for email %s" % email) 
        sys.exit(1)

    with transaction.manager:
        add_new_photos(user, storage, base_dir)
    

        
        



