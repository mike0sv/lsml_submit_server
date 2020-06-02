import datetime
import glob
import json
import os
import warnings
from collections import defaultdict
from functools import wraps
from threading import Lock

from flask import request

from metrics import EvaluationError

LOG_SUBMITS = os.environ.get('LOG_SUBMITS', 'true') == 'true'
LOGS_DIR = os.environ.get('LOG_DIR', './logs')
os.makedirs(LOGS_DIR, exist_ok=True)
_loglock = Lock()

MAXIMUM_TRIES = int(os.environ.get('MAXIMUM_TRIES', 5))


def _origin(data=None):
    data = data or {'headers': dict(request.headers)}
    try:
        return data['headers']['Xkey']
    except KeyError:
        raise EvaluationError('no key')


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

    @property
    def is_final(self):
        return self.data['final']

    @property
    def data_path(self):
        return os.path.join(LOGS_DIR, '{}_request.csv.gzip'.format(self.id))

    @property
    def metrics(self):
        return self.data['response']['data']


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


def logs_on(default=None):
    def d(f):
        @wraps(f)
        def w(*args, **kwargs):
            if LOG_SUBMITS:
                return f(*args, **kwargs)
            return default

        return w

    return d


@logs_on()
def log_to_dir(id, df, response):
    with _loglock:
        path = '{}_response.json'.format(id)
        is_final = request.args.get('final') == 'True'
        with open(os.path.join(LOGS_DIR, path), 'w', encoding='utf8')as f:
            json.dump({
                'final': is_final,
                'response': response.json,
                'environ': {k: str(v) for k, v in request.environ.items()},
                'headers': dict(request.headers)
            }, f, ensure_ascii=False, indent=2)
        if response.status_code == 200 and is_final:
            for user_submit in [_ for user_l in _read_logs()[_origin()].values() for _ in user_l]:
                if user_submit.is_final and user_submit.id != id:
                    data_path = user_submit.data_path
                    if os.path.isfile(data_path):
                        os.remove(data_path)

            path = '{}_request.csv.gzip'.format(id)
            df.to_csv(os.path.join(LOGS_DIR, path), index=False, compression='gzip')


@logs_on([])
def user_logs():
    with _loglock:
        logs = _read_logs()
        return logs[_origin()][_date()]


@logs_on()
def check_tries():
    if len(user_logs()) >= MAXIMUM_TRIES:
        raise EvaluationError('too many tries')


def user_logs_formatted():
    import stats
    with _loglock:
        logs = _read_logs()[_origin()]
    return {
        date: [{
            'is_final': l.is_final,
            'baseline_beaten': stats.baseline_beated(l),
            'metrics': l.metrics
        } for l in date_logs] for date, date_logs in logs.items()
    }
