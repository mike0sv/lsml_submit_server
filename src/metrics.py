import os

import pandas as pd
from sklearn.metrics import mean_squared_error as mse, mean_absolute_error as mae

TEST_Y_PATH = os.environ.get('YPATH', './test_y.csv')
testY = pd.read_csv(TEST_Y_PATH).set_index('id').sort_index()


class EvaluationError(ValueError):
    pass


def validate_data(df):
    if len(df) != len(testY):
        raise EvaluationError('data must have {} rows'.format(len(testY)))
    elif set(df.columns) != set(testY.columns).union([testY.index.name]):
        raise EvaluationError('data must have columns {}'.format(list(testY.columns)))
    elif set(df[testY.index.name]) != set(testY.index):
        raise EvaluationError('data have wrong ids')


def rmspe(true, pred):
    percent = abs(true - pred).astype(float) / true * 100.
    return (percent ** 2).mean() ** .5


def mape(true, pred):
    percent = abs(true - pred).astype(float) / abs(true) * 100.
    return percent.mean()


def rmse(true, pred):
    return mse(true, pred) ** 0.5


def eval_data(df):
    df = df.set_index(testY.index.name)
    df = df.sort_index()
    ef = [rmspe, mape, mse, rmse, mae]
    return {f.__name__: f(testY.views, df.views) for f in ef}
