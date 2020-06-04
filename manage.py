from flask_script import Manager

from app import create_app, Config, Repo

app = create_app()
manager = Manager(app)


@manager.command
def add_repo():
    name = input('Sync item name:')
    git_url = input('Git URL:')
    view_path = input('Mirror view path (default is "/"):') or '/'

    Config.repos[name] = {
        'git_url': git_url,
        'view_path': view_path,
    }

    Config.save()


@manager.command
def sync():
    name = input('Sync item name:')
    Repo(name).sync()


if __name__ == '__main__':
    manager.run()
