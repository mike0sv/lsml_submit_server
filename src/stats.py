from collections import defaultdict

from req_logs import _read_logs, RLog

BASELINE = {
    'mape': 15.707128974856676,
    'mean_absolute_error': 1.219070382113261,
    'mean_squared_error': 2.4324378881170055,
    'rmse': 1.5596274837655963,
    'rmspe': 23.50065988751091
}
METRICS = list(BASELINE.keys())


def baseline_beated(log: RLog):
    return all(v <= BASELINE[k] for k, v in log.metrics.items())


def describe(log: RLog):
    return '{} {}'.format(baseline_beated(log), log.is_final)


def fingerprint(log: RLog):
    return tuple(f'{log.metrics[m]:.5}' for m in METRICS)


def main():
    logs = _read_logs()
    fingerprints = defaultdict(set)
    for origin, origin_logs in logs.items():
        print(origin)
        for date in sorted(origin_logs):
            print('\t{}'.format(date))
            for log in origin_logs[date]:
                print('\t\t{}'.format(describe(log)))
                fingerprints[fingerprint(log)].add(origin)

    for fp, copies in fingerprints.items():
        if len(copies) > 1:
            print(fp, copies)


if __name__ == '__main__':
    main()
