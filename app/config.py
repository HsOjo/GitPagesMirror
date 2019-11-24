import os
from typing import Dict

from app.utils.object_convert import *

CONFIG_PATH = './config.json'


class Config:
    path_repos = './repos'
    sync_path = '/sync'
    web_hook_secret = ''
    repos = {}  # type: Dict[str, Dict[str, object]]
    default_page = [
        'index.html',
        'index.htm',
        'default.html',
        'default.htm',
    ]

    @staticmethod
    def load():
        if not os.path.exists(CONFIG_PATH):
            return

        with open(CONFIG_PATH, 'r', encoding='utf8') as io:
            json_str = io.read()
        dict_to_object(from_json(json_str), Config)

    @staticmethod
    def save():
        json_str = to_json(object_to_dict(Config))
        with open(CONFIG_PATH, 'w', encoding='utf8') as io:
            io.write(json_str)
