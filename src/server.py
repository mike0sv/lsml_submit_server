import json
import os
import random
import time

import pandas as pd
from flask import Flask, request, jsonify
from sklearn.metrics import mean_squared_error as mse, mean_absolute_error as mae

app = Flask(__name__)

LOGS_DIR = os.environ.get('LOG_DIR', './logs')
os.makedirs(LOGS_DIR, exist_ok=True)

TEST_Y_PATH = os.environ.get('YPATH', './test_y.csv')
testY = pd.read_csv(TEST_Y_PATH)


class ValidationError(ValueError):
    pass


@app.errorhandler(ValidationError)
def error_handler(error):
    return jsonify({
        'ok': False,
        'msg': error.args[0]
    }), 400


def log_to_dir(id, response):
    resp = '{}_response.json'.format(id)
    with open(os.path.join(LOGS_DIR, resp), 'w', encoding='utf8')as f:
        json.dump({
            'response': response.json,
            'environ': {k: str(v) for k, v in request.environ.items()}
        }, f, ensure_ascii=False, indent=2)
    if response.status_code == 200:
        req = '{}_request.csv.gzip'.format(id)
        pd.read_json(request.json).to_csv(os.path.join(LOGS_DIR, req), index=False, compression='gzip')


@app.after_request
def log_data(response):
    id = '{}_{}'.format(int(time.time()), random.randint(0, 100))
    log_to_dir(id, response)

    return response


def validate_data(df):
    if len(df) != len(testY):
        raise ValidationError('data must have {} rows'.format(len(testY)))
    elif set(df.columns) != set(testY.columns):
        raise ValidationError('data must have columns {}'.format(list(testY.columns)))
    elif set(df.id) != set(testY.id):
        raise ValidationError('data have wrong ids')


def rmspe(true, pred):
    percent = abs(true - pred).astype(float) / true * 100.
    return (percent ** 2).mean() ** .5


def mape(true, pred):
    percent = abs(true - pred).astype(float) / abs(true) * 100.
    return percent.mean()


def rmse(true, pred):
    return mse(true, pred) ** 2


def eval_data(df):
    ef = [rmspe, mape, mse, rmse, mae]
    return {f.__name__: f(testY.views, df.views) for f in ef}


@app.route('/eval', methods=['POST'])
def evaluate():
    data = request.json
    df = pd.read_json(data)
    validate_data(df)
    return jsonify({
        'ok': True,
        'data': eval_data(df)
    })


def main():
    app.run('0.0.0.0', 5000)


if __name__ == '__main__':
    main()
