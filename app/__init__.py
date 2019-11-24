import os
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

    if not os.path.exists(Config.path_repos):
        os.makedirs(Config.path_repos, exist_ok=True)

    return app
