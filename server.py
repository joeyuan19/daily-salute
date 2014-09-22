import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options


define("port", default=15210, help="run on the given port", type=int)


def load_index():
    with open('index.html','r') as f:
        content = ''.join(i for i in f)
    return content


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(load_index())

settings = {'debug': True}


if __name__ == "__main__":
    tornado.options.parse_command_line()

    app = tornado.web.Application(
        [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': '/home/joeyuan19/webapps/daily_salute/daily-salute/static'}),
            (r'/', IndexHandler)

        ], **settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



