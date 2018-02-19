import gunicorn.app.base
from pathlib import Path
from gunicorn.six import iteritems
from .utils import number_of_workers


class ClientAuthApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app, ca_path: Path, cert_path: Path, key_path: Path,
                 hostname=None, port=None, num_workers=None, timeout=None):
        hostname = 'localhost' if not hostname else hostname
        port = 443 if not port else port
        timeout = 30 if not timeout else timeout
        num_workers = number_of_workers() if not num_workers else num_workers
        self.options = {
            'bind': '{}:{}'.format(hostname, port),
            'workers': num_workers,
            'worker_class': 'passwords.client_auth_worker.CustomSyncWorker',
            'timeout': timeout,
            'ca_certs': str(ca_path),
            'certfile': str(cert_path),
            'keyfile': str(key_path),
            'cert_reqs': 2,
            'do_handshake_on_connect': True
        }
        self.application = app
        super().__init__()

    def init(self, parser, opts, args):
        return super().init(parser, opts, args)

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
