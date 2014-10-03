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
from helper import avoid_incomplete_tag

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
        return None

def get_draft(poem_id):
    try:
        poem = Poem.load_draft(poem_id).getData()
        return poem
    except:
        print traceback.format_exc()
        return None

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

class AdminManageContentHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self):
        opts = {}
        self.render('manage_content.html',**opts)

class AdminManageHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self,_type):
        opts = {}
        if _type == "poems":
            poems = [
                {
                    "poem_id":i[0],
                    "title":i[1],
                    "date":i[2],
                    "preview":avoid_incomplete_tag(i[3][:30])+'...'
                } for i in Poem.getPoemPage(0,5)]
            drafts = [
                {
                    "poem_id":i[0],
                    "title":i[1],
                    "date":i[2],
                    "preview":avoid_incomplete_tag(i[3][:30])+'...'
                } for i in Poem.getDraftPage(0,5)]
            opts = {
                'poems':poems,
                'more_poems':Poem.getMaxID() > 5,
                'drafts':drafts,
                'more_drafts':Poem.getMaxDraftID() > 5,
            }
            self.render('manage_poems.html',**opts)
        elif _type == "content":    
            self.render('',**opts)

class AdminHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self):
        opts = {}
        self.render('admin.html',**opts)
    
class AdminCreateHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('create.html')
    
    @tornado.web.authenticated
    def post(self):
        _json = {
            "poem":self.get_argument("poem"),
            "date":self.get_argument("date"),
            "title":self.get_argument("title"),
            "type":self.get_argument("type"),
        }
        p = Poem(_json["title"],_json["date"],_json["poem"],_json["type"],new=True)
        p.save(_json["type"])
        if _json["type"] == "draft":
            msg = "Draft saved " + datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
        elif _json["type"] == "poem":
            msg = "Poem saved " + datetime.datetime.now().strftime("%H:%M  %m/%d/%Y")
            self.write(json.dumps({"status":"redirect","msg":"saved","url":"/admin/edit/"+_json["type"]+"/"+str(p.poem_id)+"?transfer=true&create=true"}))

class AdminEditHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self,_type,poem_id):
        if _type == "draft":
            poem = get_draft(poem_id)
            if poem is None:
                self.redirect('/admin/list/poems')
        elif _type == "poem":
            poem = get_poem(poem_id)
            if poem is None:
                self.redirect('/admin/list/drafts')
        else:
            self.redirect('/admin/list/poems')
        self.render('edit.html',**poem)

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
            msg = "Poem saved as draft " + datetime.datetime.now().strftime("%H:%M  %m/%d/%Y")
        elif _json["type"] == "poem":
            msg = "Poem saved " + datetime.datetime.now().strftime("%H:%M  %m/%d/%Y")
        status = "success"
        if _type == _json["type"]:
            self.set_header("Content-Type","application/json")
            self.write(json.dumps({"status":status,"msg":msg}))
        else:
            self.write(json.dumps({"status":"redirect","msg":"saved","url":"/admin/edit/"+_json["type"]+"/"+str(p.poem_id)+"?transfer=true"}))
    
    @tornado.web.authenticated
    def delete(self,_type,poem_id):
        if _type == "poem":
            print "delete poem"
            Poem.deletePoem(poem_id)
            self.write(json.dumps({"status":"success"}))
        elif _type == "draft":
            print "delete draft"
            Poem.deleteDraft(poem_id)
            self. write(json.dumps({"status":"success"}))
        else:
            self.write(json.dumps({"status":"failed"}))
    

class AdminListHandler(AuthenticatedHandler):
    @tornado.web.authenticated
    def get(self,_type,page):
        try:
            page = max(0,int(page)-1)
        except:
            page = 0
        opts = {
            "type":_type,
            "page":page+1,
            "capitalize":lambda s: s[0].upper()+s[1:]
        }
        if _type == "poems":
            opts["collection"] = [
                {
                    "poem_id":i[0],
                    "title":i[1],
                    "date":i[2],
                    "preview":avoid_incomplete_tag(i[3][:30])+'...'
                } for i in Poem.getPoemPage(page,10)]
            opts["page_range"] = [1,Poem.getMaxID()+1]
        elif _type == "drafts":
            opts["collection"] = [
                {
                    "poem_id":i[0],
                    "title":i[1],
                    "date":i[2],
                    "preview":avoid_incomplete_tag(i[3][:30])+'...'
                } for i in Poem.getDraftPage(page,10)]
            opts["page_range"] = [1,Poem.getMaxDraftID()+1]
        else:
            self.redirect('/admin')
        lower_limit = max(1,page-2)
        upper_limit = min(lower_limit+4,opts["page_range"][1]/10+1)
        opts["page_range"] = (lower_limit,upper_limit)
        self.render('list.html',**opts)
    
    @tornado.web.authenticated
    def post(self,_type,page):
        original_id = int(self.get_argument('from'))
        new_id = min(max(int(self.get_argument('to')),1),Poem.getMaxID())
        print new_id,original_id
        Poem.movePoem(original_id,new_id)
        print "done moving"
        new_page = (Poem.getMaxID()-new_id)/10
        print new_id
        self.write(json.dumps({"page":str(new_page)}))

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
            if self.get_argument("from_logout",default=False):
                opts["alert"] = "logout"
        except tornado.web.MissingArgumentError:
            pass
        self.render('login.html',**opts)

    def post(self):
        opts = {"error":"none","error_message":"","alert":"none"}
        try:
            uname = self.get_argument("username")
            if len(uname) == 0: raise tornado.web.MissingArgumentError()
        except tornado.web.MissingArgumentError:
            opts["error"] = "user"
            opts["alert"] = "user"
            opts["error_message"] = "User field cannot be empty"
            self.render('login.html',**opts)
        try:
            passw = self.get_argument("password")
            if len(passw) == 0: raise tornado.web.MissingArgumentError()
        except tornado.web.MissingArgumentError:
            opts["alert"] = "password"
            opts["error"] = "password"
            opts["error_message"] = "Password field cannot be empty"
            self.render('login.html',**opts)
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
            self.render('login.html',**opts)

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
            (r'/admin/edit/([a-zA-Z]+)/([0-9]+)',AdminEditHandler),
            (r'/admin/list/([a-zA-Z]+)(?:/([0-9]+))?',AdminListHandler),
            (r'/admin/create',AdminCreateHandler),
            (r'/admin/manage/(.*)',AdminManageHandler),
            (r'/admin',AdminHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path':static_path}),
            (r'/poem/random', RandomPoemHandler),
            (r'/poem/([0-9]+)', PoemHandler),
            (r'/', IndexHandler),
        ], **app_settings
    )
    http_server = tornado.httpserver.HTTPServer(app,**server_settings)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



