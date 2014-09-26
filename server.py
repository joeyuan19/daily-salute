import os.path
import re
import random
import traceback

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options

from db import Poem, getLatestID

def get_poem(poem_id):
    try:
        poem = Poem.load(poem_id).getData()
        if len(poem['poem_title']) == 0:
            poem['poem_title'] = poem['poem_date']
            poem['poem_date'] = ''
        return poem
    except:
        print traceback.format_exc()
        return {}

def render_poem(poem_id):
    return renderFromHTMLFile('poem.tmpl.html',get_poem(poem_id))

def render_page(poem_id):
    if poem_id == 1:
        prev_page = 1
    else:
        prev_page = poem_id - 1
    if poem_id == getLatestID():
        next_page = getLatestID()
    else:
        next_page = poem_id + 1
    
    return renderFromHTMLFile('index.html',{
        'page_content':render_poem(poem_id),
        'prev_page':prev_page,
        'next_page':next_page
    })

def renderFromHTMLFile(filepath,variables):
    with open(filepath,'r') as f:
        template = ''.join(i for i in f)
    return renderHTML(template,variables)

def renderHTML(template,variables):
    for key,val in variables.iteritems():
        template = re.sub(r'\{\{'+str(key)+'\}\}',str(val),template)
    template = re.sub(r'\{\{.*?\}\}','',template)
    return template

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(render_page(getLatestID()))

class PoemHandler(tornado.web.RequestHandler):
    def get(self,poem_id):
        try:
            poem_id = int(poem_id)
            if poem_id > getLatestID():
                print 'redirect greater than limit'
                self.redirect('/poem/'+str(getLatestID()))
            if poem_id < 1:
                print 'redirect less than limit'
                self.redirect('/poem/1')
            page_content = render_page(poem_id)
            print 'redirect greater than limit'
            self.write(page_content)
        except:
            print traceback.format_exc()
            self.redirect('/')

class RandomPoemHandler(tornado.web.RequestHandler):
    def get(self):
        rand_poem = int(round(1. + (getLatestID()-1)*random.random()))
        self.redirect('/poem/'+str(rand_poem))

if __name__ == "__main__":
    define("port", default=15210, help="run on the given port", type=int)
    define("local", default=False, help="designates whether instance is run on the local/server", type=bool)
    tornado.options.parse_command_line()

    static_file_path = '/home/joeyuan19/webapps/daily_salute/daily-salute/static'
    if options.local:
        static_file_path = './static'
        
    app = tornado.web.Application(
        [
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path':static_file_path}),
            (r'/poem/random', RandomPoemHandler),
            (r'/poem/(.*)', PoemHandler),
            (r'/', IndexHandler),
        ], debug=options.local
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



