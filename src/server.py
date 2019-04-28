import io
import random
import time

import pandas as pd
from flask import Flask, request, jsonify

from metrics import eval_data, validate_data, EvaluationError
from req_logs import log_to_dir, check_tries

app = Flask(__name__)


@app.errorhandler(EvaluationError)
def error_handler(error):
    return jsonify({
        'ok': False,
        'msg': error.args[0]
    }), 400


@app.after_request
def log_data(response):
    id = '{}_{}'.format(int(time.time()), random.randint(0, 100))
    log_to_dir(id, _get_df(), response)

    return response


def _get_df():
    if hasattr(request, 'df_'):
        return request.df_
    submit = request.files['submit']
    buf = io.BytesIO(submit.read())
    df = pd.read_csv(buf, compression='gzip')
    request.df_ = df
    return df


@app.route('/eval', methods=['POST'])
def evaluate():
    check_tries()
    df = _get_df()
    validate_data(df)
    return jsonify({
        'ok': True,
        'data': eval_data(df)
    })


def main():
    app.run('0.0.0.0', 5000)


if __name__ == '__main__':
    main()
