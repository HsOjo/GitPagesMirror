import hmac
import os
import threading
import traceback

import git
from flask import Blueprint, request, send_file, abort

from app.common import *
from app.config import Config


class Repo:
    def __init__(self, name):
        self.info = Config.repos[name]

        self.name = name
        self.mirror_dir = '%s/%s' % (Config.path_repos, name)

        self.blueprint = self.g_blueprint()
        self._status = 0  # 0: idle, 1: syncing
        self._lock = threading.Lock()

    def g_blueprint(self):
        blueprint = Blueprint(
            self.name, self.name, url_prefix=self.info['view_path'],
        )

        def view_mirror(path: str = ''):
            path = os.path.join(self.mirror_dir, self.info.get('source_folder', ''), path)

            if os.path.exists(path):
                if os.path.isdir(path):
                    for page in Config.default_page:
                        path_page = os.path.join(path, page)
                        if os.path.exists(path_page) and os.path.isfile(path_page):
                            path = path_page
                            break

                if not os.path.isfile(path):
                    return abort(403)
            else:
                return abort(404)

            return send_file(os.path.abspath(path))

        blueprint.add_url_rule('/', view_func=view_mirror)
        blueprint.add_url_rule('/<path:path>', view_func=view_mirror)

        @blueprint.route(Config.sync_path, methods=['GET', 'POST'])
        def sync():
            if Config.web_hook_secret != '':
                sign = request.headers.get('X-Hub-Signature', '')
                count_sign = hmac.new(Config.web_hook_secret.encode(), request.get_data(), 'sha1').hexdigest()
                count_sign = 'sha1=%s' % count_sign
                if count_sign != sign:
                    return abort(403)

            threading.Thread(target=self._sync).start()
            return 'Syncing %s at %s.' % (self.name, get_current_time())

        return blueprint

    def sync(self):
        with self._lock:
            status = self._status

        if status == 0:
            threading.Thread(target=self._sync).start()

    def _sync(self):
        with self._lock:
            if self._status != 0:
                return
            self._status = 1

        self.print('Sync start at %s.' % get_current_time())

        while True:
            try:
                if not os.path.exists(self.mirror_dir):
                    git.Repo.clone_from(url=self.info['git_url'], to_path=self.mirror_dir)
                else:
                    git.Repo(self.mirror_dir).remote().fetch()
                    git.Repo(self.mirror_dir).head.reset(working_tree=True)
                break
            except:
                traceback.print_exc()
                self.print('Sync failed at %s, retry.' % get_current_time())

        self.print('Sync finish at %s.' % get_current_time())

        with self._lock:
            self._status = 0

    def print(self, content):
        print('[%s] %s' % (self.name, content))
