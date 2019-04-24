from pprint import pprint

import requests


class EvalClient:
    def __init__(self, host='localhost', port=5000):
        self.port = port
        self.host = host
        self._url = 'http://{}:{}/eval'.format(host, port)

    def make_eval(self, df):
        r = requests.post(self._url, json=df.to_json())
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 400:
            raise ValueError(r.json()['msg'])
        else:
            r.raise_for_status()


_ec = EvalClient()


def make_eval(df):
    return _ec.make_eval(df)


def main():
    import pandas as pd
    data = pd.DataFrame([
        {'id': 1, 'views': 8},
        {'id': 2, 'views': 8},
        {'id': 3, 'views': 8},
    ])

    pprint(make_eval(data))


if __name__ == '__main__':
    main()
