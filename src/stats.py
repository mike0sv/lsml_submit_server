from req_logs import _read_logs, RLog

BASELINE = {
    'mape': 15.707128974856676,
    'mean_absolute_error': 1.219070382113261,
    'mean_squared_error': 2.4324378881170055,
    'rmse': 1.5596274837655963,
    'rmspe': 23.50065988751091
}


def baseline_beated(log: RLog):
    return all(v <= BASELINE[k] for k, v in log.metrics.items())


def describe(log: RLog):
    return '{} {}'.format(baseline_beated(log), log.is_final)


def main():
    logs = _read_logs()

    for origin, origin_logs in logs.items():
        print(origin)
        for date in sorted(origin_logs):
            print('\t{}'.format(date))
            for log in origin_logs[date]:
                print('\t\t{}'.format(describe(log)))


if __name__ == '__main__':
    main()
