from fabric import api

api.env.hosts = ['178.79.185.15']


def shell():

    api.open_shell()


def deploy():

    with api.cd(api.env.deploy_path):

        api.run("git pull")
        api.run("%s/pip install -r requirements.txt" % api.env.python_path)
        api.run("%s/python setup.py develop" % api.env.python_path)
        api.run("%s/drop_test_db" % api.env.python_path)
        api.run("%s/python setup.py test" % api.env.python_path)
        api.run("%s/alembic upgrade head" % api.env.python_path)
        api.sudo("supervisorctl restart photoapp")
