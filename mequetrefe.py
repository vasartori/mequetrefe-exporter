import argparse
import yaml
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer


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


def start():
    args = cmd_args()
    cfg = read_config_file(args.config_file)
    return get_metrics(cfg)


class HTTPServer_RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = start()
        for k, v in message.items():
            self.wfile.write(bytes("# HELP " + k + " Default\r\n", "utf8"))
            self.wfile.write(bytes("# TYPE " + k + " summary\r\n", "utf8"))
            self.wfile.write(bytes(str(k) + ' ' + str(v) + "\r\n", "utf8"))
        return


if __name__ == '__main__':
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, HTTPServer_RequestHandler)
    httpd.serve_forever()
