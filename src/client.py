import shutil
import tempfile
from pprint import pprint

import requests


class EvalClient:
    def __init__(self, host='localhost', port=5000):
        self.port = port
        self.host = host
        self._url = 'http://{}:{}/eval'.format(host, port)

    def make_eval(self, df):
        filename = tempfile.mktemp('_submit.csv.gz')
        try:
            df.to_csv(filename, compression='gzip', header=True)
            with open(filename, 'rb') as submit:
                r = requests.post(self._url, files={'submit': submit})
        finally:
            shutil.rmtree(filename, True)

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 400:
            raise ValueError(r.json()['msg'])
        else:
            r.raise_for_status()


_ec = EvalClient('35.231.19.141', 8000)


def make_eval(df):
    return _ec.make_eval(df)


def main():
    import pandas as pd
    data = pd.DataFrame([
        {'id': 1, 'views': 8},
        {'id': 2, 'views': 8},
        {'id': 3, 'views': 8},
    ])
    data = data.set_index('id')

    pprint(EvalClient().make_eval(data.views))


if __name__ == '__main__':
    main()
