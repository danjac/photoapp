from fabric import api

api.env.hosts = ['178.79.185.15']


def shell():

    api.open_shell()


def deploy():

    with api.cd(api.env.deploy_path):

        # deploy update
        api.run("git pull")
        api.run("%s/python setup.py develop" % api.env.python_path)

        # run tests: drop test DB to ensure clean run
        api.run("%s/drop_test_db" % api.env.python_path)
        api.run("%s/python setup.py test" % api.env.python_path)

        # run migrations
        api.run("%s/alembic upgrade head" % api.env.python_path)

        # restart long-running processes
        api.sudo("/etc/init.d/memcached restart")
        api.sudo("supervisorctl restart photoapp")
