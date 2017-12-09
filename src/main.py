import threading
import http.server
import logging

KEY_APP_NAME = 'app.name'
KEY_HTTP_MONITORING_PORT='app.http.monitoring'
KEY_PLUGINS='app.plugins'


class HttpHeartBeatRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        message='OK'.encode('utf-8')
        self.wfile.write(bytes(message))
        return


def main():
    app = read_config()

    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] : (%(threadName)-9s) %(message)s', )

    logging.log(logging.INFO, 'Starting application ' + app[KEY_APP_NAME])
    plugins = threading.Thread(name='daemon2', target=plugin_loader(app))
    heartbeat = threading.Thread(name='daemon', target=setup_http_heartbeat(app[KEY_HTTP_MONITORING_PORT]))

    plugins.start()
    plugins.join()
    heartbeat.start()
    heartbeat.join()


def read_config(config='../config/config.ini'):
    app = {}
    config_file = open(config, 'r')
    for line in config_file:
        if line[0] != '#':
            if ';' in line.split('=')[1]:
                app[line.split('=')[0]] = line.split('=')[1].split(';')
            else:
                app[line.split('=')[0]] = line.split('=')[1]

    return app


def setup_http_heartbeat(port=8000):
    httpd = http.server.HTTPServer(('127.0.0.1', int(port)), HttpHeartBeatRequestHandler)

    logging.log(logging.INFO, 'http monitoring on port : ' + port)
    httpd.serve_forever()


def plugin_loader(app=[]):
    logging.log(logging.INFO, 'plugin loader initiated')
    for plugin in app[KEY_PLUGINS]:
        logging.log(logging.INFO, 'importing module : ' + plugin)
        __import__(plugin)


if __name__ == '__main__':
    main()
