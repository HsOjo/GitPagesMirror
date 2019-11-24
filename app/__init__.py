from typing import List

from flask import Flask

from app.config import Config
from app.repo import Repo

repos = []  # type: List[Repo]


def create_app():
    app = Flask(__name__)
    Config.load()

    for repo_name in Config.repos:
        repo = Repo(repo_name)
        app.register_blueprint(repo.blueprint)
        repos.append(repo)

    return app
