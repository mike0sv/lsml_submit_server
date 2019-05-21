from req_logs import _read_logs, RLog

BASELINE = {
    u'mape': 16.913420278704557,
    u'mean_absolute_error': 1.2826925308727513,
    u'mean_squared_error': 2.8833770868964472,
    u'rmse': 1.6980509671080097,
    u'rmspe': 24.390528393231794
}


def baseline_beated(log: RLog):
    return all(v <= BASELINE[k] for k, v in log.metrics .items())


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
