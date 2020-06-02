import shutil
import tempfile
from pprint import pprint
import getpass
import requests


class EvalClient:
    def __init__(self, host='localhost', port=5000):
        self.port = port
        self.host = host
        self._url = 'https://{}:{}/'.format(host, port)
        self.password = getpass.getpass()

    def make_eval(self, df, final=False):
        filename = tempfile.mktemp('_submit.csv.gz')
        try:
            df.to_csv(filename, compression='gzip', header=True)
            with open(filename, 'rb') as submit:
                r = requests.post(self._url + 'eval', params={'final': final}, files={'submit': submit},
                                  auth=(getpass.getuser(), self.password))
        finally:
            shutil.rmtree(filename, True)

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 400:
            raise ValueError(r.json()['msg'])
        else:
            r.raise_for_status()

    def check_results(self):
        r = requests.get(self._url + 'result', auth=(getpass.getuser(), self.password))
        r.raise_for_status()
        return r.json()


_ec = EvalClient('jn.hse.aigmx.com', 443)


def make_eval(df, final=False):
    return _ec.make_eval(df, final)


def check_results():
    return _ec.check_results()


def main():
    import pandas as pd
    data = pd.DataFrame([
        {'id': 1, 'views': 8},
        {'id': 2, 'views': 8},
        {'id': 3, 'views': 8},
    ])
    data = data.set_index('id')

    pprint(_ec.make_eval(data.views, final=True))


if __name__ == '__main__':
    main()
