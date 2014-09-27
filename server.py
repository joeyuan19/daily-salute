import os.path
import re
import random
import traceback

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.template

from tornado.options import define, options

from db import Poem

DEBUG = True

def load_cookie_secret():
    with open('cookie_secret.txt','r') as f:
        content = ''.join(i.strip() for i in f).strip()
    return content

def get_poem(poem_id):
    try:
        poem = Poem.load(poem_id).getData()
        if len(poem['poem_title']) == 0:
            poem['poem_title'] = poem['poem_date']
            poem['poem_date'] = ''
        return poem
    except:
        return {}

def render_page(poem_id):
    if poem_id == 1:
        prev_page = 1
    else:
        prev_page = poem_id - 1
    if poem_id == Poem.getMaxID():
        next_page = Poem.getMaxID()
    else:
        next_page = poem_id + 1
    poem = get_poem(poem_id)
    poem['prev_page'] = prev_page
    poem['next_page'] = next_page
    loader = tornado.template.Loader('./')
    return loader.load('index.html').generate(**poem)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(render_page(Poem.getMaxID()))

class PoemHandler(tornado.web.RequestHandler):
    def get(self,poem_id):
        try:
            poem_id = int(poem_id)
            if poem_id > Poem.getMaxID():
                self.redirect('/poem/'+str(Poem.getMaxID()))
                return
            if poem_id < 1:
                self.redirect('/poem/1')
                return
            self.write(render_page(poem_id))
        except:
            print traceback.format_exc()
            self.redirect('/')

class RandomPoemHandler(tornado.web.RequestHandler):
    def get(self):
        rand_poem = int(round(1. + (Poem.getMaxID()-1)*random.random()))
        self.redirect('/poem/'+str(rand_poem))

class AuthenticatedHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class AdminHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)

class AdminEditHandler(AuthenticatedHandler):
    def get(self):
        pass

class AuthLogoutHandler(AuthenticatedHandler):
    def get(self):
        pass

class AuthLoginHandler(AuthenticatedHandler):
    def get(self):
        t = self.render('admin.html')
        self.write(t)

    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/admin")

if __name__ == "__main__":
    define("port", default=15210, help="run on the given port", type=int)
    define("local", default=False, help="designates whether instance is run on the local/server", type=bool)
    tornado.options.parse_command_line()

    static_file_path = '/home/joeyuan19/webapps/daily_salute/daily-salute/static'
    if options.local:
        static_file_path = './static'
    
    settings = {
        "debug":DEBUG,
        "cookie_secret":load_cookie_secret(),
        "login_url":"/auth/login",
        "xsrf_cookies":True,
    }
    
    app = tornado.web.Application(
        [
            (r'/auth/login',AuthLoginHandler),
            (r'/auth/logout',AuthLogoutHandler),
            (r'/admin',AdminHandler),
            (r'/admin/edit/(.*)',AdminEditHandler),
            (r'/admin',AdminHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path':static_file_path}),
            (r'/poem/random', RandomPoemHandler),
            (r'/poem/(.*)', PoemHandler),
            (r'/', IndexHandler),
        ], **settings
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



