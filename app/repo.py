import hmac
import os
import shutil
import threading
import traceback

import git
from flask import Blueprint, request, send_file, abort
from git import GitCommandError

from app.common import *
from app.config import Config


class MyProgressPrinter(git.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")


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

        def view_mirror(_: str = None):
            req_path = request.path.replace(self.info['view_path'], '', 1)
            if req_path != '' and req_path[0] == '/':
                req_path = req_path[1:]

            path = os.path.join(self.mirror_dir, self.info.get('source_folder', ''), req_path)

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

        for r, _, _ in os.walk(self.mirror_dir):
            path = r.replace(self.mirror_dir, '')
            if '/.git' == path[:5]:
                continue

            blueprint.add_url_rule('%s' % path, view_func=view_mirror)
            blueprint.add_url_rule('%s/' % path, view_func=view_mirror)
            blueprint.add_url_rule('%s/<string:_>' % path, view_func=view_mirror)

        blueprint.add_url_rule('/', view_func=view_mirror)

        @blueprint.route(Config.sync_path, methods=['GET', 'POST'])
        def sync():
            if Config.web_hook_secret != '':
                sign = request.headers.get('X-Hub-Signature', '')
                count_sign = hmac.new(Config.web_hook_secret.encode(), request.get_data(), 'sha1').hexdigest()
                count_sign = 'sha1=%s' % count_sign
                if count_sign != sign:
                    return abort(403)

            threading.Thread(target=self._sync).start()
            return 'Now Syncing...'

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

        print('[%s] Sync Start.' % get_current_time())

        while True:
            try:
                if not os.path.exists(self.mirror_dir):
                    git.Repo.clone_from(url=self.info['git_url'], to_path=self.mirror_dir)
                else:
                    git.Repo(self.mirror_dir).remote().pull()
                break
            except GitCommandError:
                shutil.rmtree(self.mirror_dir)
            except:
                traceback.print_exc()
                print('[%s] Sync Failed, Retry.' % get_current_time())

        print('[%s] Sync Finish.' % get_current_time())

        with self._lock:
            self._status = 0
