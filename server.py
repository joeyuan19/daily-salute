import os.path
import re
import random
import json
import datetime
import traceback

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.template
from tornado.options import define, options

from db import Poem, User

DEBUG = True

def load_cookie_secret():
    with open('cookie_secret.txt','r') as f:
        content = ''.join(i.strip() for i in f).strip()
    return content

def get_poem(poem_id):
    try:
        poem = Poem.load(poem_id).getData()
        return poem
    except:
        print traceback.format_exc()
        return {}

def get_draft(poem_id):
    try:
        poem = Poem.load_draft(poem_id).getData()
        return poem
    except:
        return {}

def load_page_vars(poem_id):
    if poem_id == 1:
        prev_page = 1
    else:
        prev_page = poem_id - 1
    if poem_id == Poem.getMaxID():
        next_page = Poem.getMaxID()
    else:
        next_page = poem_id + 1
    poem = get_poem(poem_id)
    print poem,poem_id
    if len(poem['poem_title']) == 0:
        poem['poem_title'] = poem['poem_date']
        poem['poem_date'] = ''
    poem['prev_page'] = prev_page
    poem['next_page'] = next_page
    return poem 

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html',**load_page_vars(Poem.getMaxID()))

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
            self.render('index.html',**load_page_vars(poem_id))
        except:
            print traceback.format_exc()
            self.redirect('/')

class RandomPoemHandler(tornado.web.RequestHandler):
    def get(self):
        rand_poem = int(round(1. + (Poem.getMaxID()-1)*random.random()))
        self.redirect('/poem/'+str(rand_poem))

class AuthenticatedHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("DS_SESSION_TOKEN")

class AdminHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.render('admin.html')

class AdminEditHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self,_type,poem_id):
        if _type == "draft":
            poem = get_draft(poem_id)
            self.render('edit.html',**poem)
        elif _type == "poem":
            poem = get_poem(poem_id)
            self.render('edit.html',**poem)
        else:
            self.redirect('/admin/poem_list')

    @tornado.web.authenticated
    def post(self,_type,poem_id):
        poem_id = int(poem_id)
        _json = {
            "poem":self.get_argument("poem"),
            "date":self.get_argument("date"),
            "title":self.get_argument("title"),
            "type":self.get_argument("type"),
        }
        p = Poem(_json["title"],_json["date"],_json["poem"],_type,new=False,poem_id=poem_id)
        p.save(_json["type"])
        if _json["type"] == "draft":
            msg = "Poem saved as draft " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        elif _json["type"] == "poem":
            msg = "Poem saved " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        status = "success"
        if _type == _json["type"]:
            self.set_header("Content-Type","application/json")
            self.write(json.dumps({"status":status,"msg":msg}))
        else:
            self.redirect("/admin/edit/"+_json["type"]+"/"+p.poem_id+"?transfer=true")

class AuthLogoutHandler(AuthenticatedHandler):
    def get(self):
        try:
            self.clear_cookie("DS_SESSION_TOKEN")
            self.redirect('/auth/login?from_logout=True')
        except:
            self.redirect('/auth/login')

class AuthLoginHandler(AuthenticatedHandler):
    def get(self):
        opts = {"error":"none","error_message":"","alert":"none"}
        try:
            if self.get_argument("from_logout"):
                opts["alert"] = "logout"
        except tornado.web.MissingArgumentError:
            pass
        self.render('admin_login.html',**opts)

    def post(self):
        opts = {"error":"none","error_message":"","alert":"none"}
        try:
            uname = self.get_argument("username")
            if len(uname) == 0: raisetornado.web.MissingArgumentError()
        except tornado.web.MissingArgumentError:
            opts["error"] = "user"
            opts["alert"] = "user"
            opts["error_message"] = "User field cannot be empty"
            self.render('admin_login.html',**opts)
        try:
            passw = self.get_argument("password")
            if len(passw) == 0: raisetornado.web.MissingArgumentError()
        except tornado.web.MissingArgumentError:
            opts["alert"] = "password"
            opts["error"] = "password"
            opts["error_message"] = "Password field cannot be empty"
            self.render('admin_login.html',**opts)
        token,err = User.login(uname,passw)
        if token is not None:
            self.set_secure_cookie("DS_SESSION_TOKEN", token, expires_days=7)
            try:
                url = self.get_argument("next")
                self.redirect(url)
            except:
                self.redirect("/admin")
        else:
            opts["error"] = err
            opts["alert"] = "error"
            opts["error_message"] = (lambda x: 
                "User '"+uname+"' does not exist"
                if x == "user" else 
                "Incorrect password")(err)
            self.render('admin_login.html',**opts)

if __name__ == "__main__":
    define("port", default=15210, help="run on the given port", type=int)
    define("local", default=False, help="designates whether instance is run on the local/server", type=bool)
    tornado.options.parse_command_line()
    
    static_path = os.path.join(os.curdir, "static") 
    template_path = os.path.join(os.curdir, "templates") 

    app_settings = {
        "debug":DEBUG,
        "cookie_secret":load_cookie_secret(),
        "login_url":"/auth/login",
        "xsrf_cookies":True,
        "template_path":template_path
    }
    server_settings = {
     
    }

    app = tornado.web.Application(
        [
            (r'/auth/login',AuthLoginHandler),
            (r'/auth/logout',AuthLogoutHandler),
            (r'/admin',AdminHandler),
            (r'/admin/edit/(.*)/(.*)',AdminEditHandler),
            (r'/admin',AdminHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path':static_path}),
            (r'/poem/random', RandomPoemHandler),
            (r'/poem/(.*)', PoemHandler),
            (r'/', IndexHandler),
        ], **app_settings
    )
    http_server = tornado.httpserver.HTTPServer(app,**server_settings)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



