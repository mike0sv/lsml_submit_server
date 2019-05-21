import contextlib
import os
import re
import shutil
import tempfile
import unittest
from pprint import pformat

import pandas as pd


@contextlib.contextmanager
def make_data(df):
    filename = tempfile.mktemp('_submit.csv.gz')
    try:
        try:
            df = df.set_index('id')
        except KeyError:
            pass
        df.to_csv(filename, compression='gzip', header=True)
        with open(filename, 'rb') as submit:
            yield submit
    finally:
        shutil.rmtree(filename, True)


class WrongData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['YPATH'] = '../test_y.csv'
        os.environ['LOG_SUBMITS'] = 'false'
        import server
        cls.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()

    def _eval(self, df, is_ok=False, msg_like=None, zero_error=False):
        with make_data(df) as submit:
            r = self.client.post('/eval', data={'submit': submit})
        data = r.json
        if is_ok:
            self.assertTrue(data['ok'], pformat(data))
            if zero_error:
                self.assertTrue(all(m == 0 for m in data['data'].values()), pformat(data))
        else:
            self.assertFalse(data['ok'], pformat(data))
            if msg_like:
                self.assertTrue(bool(re.match(msg_like, data['msg'])),
                                'wrong error msg "{}", \nmust be like "{}"'.format(data['msg'], msg_like))

    def _create_df(self, count, **column_values):
        df = pd.DataFrame([column_values for _ in range(count)])
        df['id'] = df.index + 1
        return df

    def test_columns(self):
        df = self._create_df(3, views=7, lol=8)
        self._eval(df, msg_like='data must have columns.*')

        df = self._create_df(3)
        self._eval(df, msg_like='data must have columns.*')

    def test_count(self):
        df = self._create_df(4, views=7)
        self._eval(df, msg_like='data must have \d+ rows')

        df = self._create_df(2, views=7)
        self._eval(df, msg_like='data must have \d+ rows')

    def test_wrong_order(self):
        import metrics
        df = metrics.testY.copy()
        df = df.sort_values('id', ascending=False)
        self._eval(df, is_ok=True, zero_error=True)

    def test_ids(self):
        df = self._create_df(3, views=7)
        df.id[0] = 5
        self._eval(df, msg_like='data have wrong ids')

    def test_ok(self):
        import metrics
        self._eval(metrics.testY, is_ok=True, zero_error=True)

    def test_results(self):
        r = self.client.get('/result')
        print(r.json)
        self.assertEqual(r.status_code, 200)
