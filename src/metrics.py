import os

import pandas as pd
from sklearn.metrics import mean_squared_error as mse, mean_absolute_error as mae

TEST_Y_PATH = os.environ.get('YPATH', './test_y.csv')
testY = pd.read_csv(TEST_Y_PATH)


class EvaluationError(ValueError):
    pass


def validate_data(df):
    if len(df) != len(testY):
        raise EvaluationError('data must have {} rows'.format(len(testY)))
    elif set(df.columns) != set(testY.columns):
        raise EvaluationError('data must have columns {}'.format(list(testY.columns)))
    elif set(df.id) != set(testY.id):
        raise EvaluationError('data have wrong ids')


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
