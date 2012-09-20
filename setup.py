import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_jinja2',
    'pyramid_webassets',
    'pyramid_beaker',
    'pyramid_tm',
    'pyramid_debugtoolbar',
    'pyramid_exclog',
    'cornice',
    'sqlalchemy',
    'zope.sqlalchemy',
    'psycopg2',
    'wtforms',
    'passlib',
    'py_bcrypt',
    'mailer',
    'webhelpers',
    'alembic',
    'PIL',
    'mock',
    'cssmin',
    'requests',
    'webtest',
    'pylibmc',
]

setup(
    name='photoapp',
    version='0.0',
    description='photoapp',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="photoapp",
    entry_points="""\
    [paste.app_factory]
    main = photoapp:main
    [console_scripts]
    initialize_photoapp_db = photoapp.scripts.initializedb:main
    drop_test_db = photoapp.scripts.drop_test_db:main
    """,
    paster_plugins=['pyramid'],
)
