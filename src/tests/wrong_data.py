import os
import re
import tempfile
import unittest

import pandas as pd


class WrongData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['YPATH'] = '../test_y.csv'
        import server
        cls.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        cls.client = server.app.test_client()

    def _eval(self, df, is_ok=False, msg_like=None):
        r = self.client.post('/eval', json=df.to_json())
        data = r.json
        if is_ok:
            self.assertTrue(data['ok'])
        else:
            self.assertFalse(data['ok'])
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

    def test_ids(self):
        df = self._create_df(3, views=7)
        df.id[0] = 5
        self._eval(df, msg_like='data have wrong ids')

    def test_ok(self):
        import server
        self._eval(server.testY, is_ok=True)
