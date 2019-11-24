import hmac
import os
import threading

import git
from flask import Blueprint, request, send_file, abort

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

        def view_mirror(filename=None):
            request_dir = os.path.dirname(request.path[1:])
            dirname = os.path.join(self.mirror_dir, request_dir)
            if filename is None:
                for page in Config.default_page:
                    path = os.path.join(dirname, page)
                    if os.path.exists(path):
                        filename = page
                        break

            if filename is None:
                return abort(404)

            path = os.path.abspath(os.path.join(dirname, filename))
            
            return send_file(path)

        for r, _, _ in os.walk(self.mirror_dir):
            path = r.replace(self.mirror_dir, '')

            rule = '%s/<string:filename>' % path
            rule_r = '%s/' % path

            blueprint.add_url_rule(rule, view_func=view_mirror)
            blueprint.add_url_rule(rule_r, view_func=view_mirror)

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

        if not os.path.exists(self.mirror_dir):
            git.Repo.clone_from(url=self.info['git_url'], to_path=self.mirror_dir)
        else:
            git.Repo(self.mirror_dir).remote().pull()

        print('[%s] Sync Finish.' % get_current_time())

        with self._lock:
            self._status = 0
