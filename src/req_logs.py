import datetime
import glob
import json
import os
import warnings
from collections import defaultdict
from threading import Lock

from flask import request

from metrics import EvaluationError

LOGS_DIR = os.environ.get('LOG_DIR', './logs')
os.makedirs(LOGS_DIR, exist_ok=True)
_loglock = Lock()

MAXIMUM_TRIES = int(os.environ.get('MAXIMUM_TRIES', 5))


def _origin(data=None):
    data = data or request.environ
    return data['REMOTE_ADDR']


def _date(date=None):
    date = date or datetime.datetime.now()
    return date.strftime('%Y-%m-%d')


class RLog:
    @staticmethod
    def from_file(path):
        id = os.path.basename(path).split('_response')[0]
        with open(path, 'r', encoding='utf8') as f:
            return RLog(id, json.load(f))

    def __init__(self, id, data):
        self.id = id
        self.data = data

    @property
    def ok(self):
        return self.data['response']['ok']

    @property
    def origin(self):
        return _origin(self.data['environ'])

    @property
    def datetime(self):
        return datetime.datetime.fromtimestamp(int(self.id.split('_')[0]))

    @property
    def date(self):
        return _date(self.datetime)


def _read_logs():
    logs = defaultdict(lambda: defaultdict(list))
    for f in glob.glob(os.path.join(LOGS_DIR, '*.json')):
        try:
            l = RLog.from_file(f)
            if l.ok:
                logs[l.origin][l.date].append(l)
        except:
            warnings.warn('cant read log {}'.format(f), )
    return logs


def log_to_dir(id, df, response):
    with _loglock:
        path = '{}_response.json'.format(id)
        with open(os.path.join(LOGS_DIR, path), 'w', encoding='utf8')as f:
            json.dump({
                'response': response.json,
                'environ': {k: str(v) for k, v in request.environ.items()}
            }, f, ensure_ascii=False, indent=2)
        if response.status_code == 200 and request.args.get('final') == 'True':
            path = '{}_request.csv.gzip'.format(id)
            df.to_csv(os.path.join(LOGS_DIR, path), index=False, compression='gzip')


def user_logs():
    with _loglock:
        logs = _read_logs()
        return logs[_origin()][_date()]


def check_tries():
    if len(user_logs()) >= MAXIMUM_TRIES:
        raise EvaluationError('too many tries')
