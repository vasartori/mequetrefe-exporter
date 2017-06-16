import argparse
import yaml
import subprocess
from prometheus_client import Metric, start_http_server, REGISTRY
import time


def cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", help="Path to config file. ",
                        required=False, default='./commands.yaml')
    return parser.parse_args()


def read_config_file(config):
    with open(config) as f:
        return yaml.load(f.read())


def get_metrics(commands):
    metrics = dict()
    for i in commands:
        for metric, command in i.items():
            metrics[metric] = int(subprocess.Popen(command, shell=True,
                                                   stdout=subprocess.PIPE).
                                  stdout.read())
    return metrics


def prepare_start():
    args = cmd_args()
    cfg = read_config_file(args.config_file)
    return get_metrics(cfg)


class Prom:
    def __init__(self, metrics):
        self.metrics = metrics

    def collect(self):
        for k, v in self.metrics.items():
            metric = Metric(k, 'teste', 'gauge')
            metric.add_sample(k, value=v, labels={})
            yield metric

if __name__ == '__main__':
    start_http_server(8000)
    REGISTRY.register(Prom(metrics=prepare_start()))
    while True:
        time.sleep(1)
