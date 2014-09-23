import os.path
import re
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options


def load_index():
    with open('index.html','r') as f:
        content = ''.join(i for i in f)
    return renderHTML(content,{'page_content':load_last_poem(),'toc_content':'<b>August</b>'})

def renderFromHTMLFile(template_path,poem):
    with open(template_path,'r') as f:
        template = ''.join(i for i in f)
    for key,val in poem.iteritems():
        template = re.sub(r'\{\{'+key+'\}\}',val,template)
    return template

def renderHTML(template,poem):
    for key,val in poem.iteritems():
        template = re.sub(r'\{\{'+key+'\}\}',val,template)
    return template
    

def load_last_poem():
    poems = [
        {
            'post_title':'post 1',
            'post_date':'9/22/14',
            'post_content':'This is the first line,<br/>it doesn\'t exactly rhyme.<br/>Just deal with it.</br>end'
        },
        {
            'post_title':'post 2',
            'post_date':'9/21/14',
            'post_content':'A second poem is just masochism'
        },
        {
            'post_title':'post 1',
            'post_date':'9/20/14',
            'post_content':'This is the next <i>poem</i>'
        }
    ]
    return renderFromHTMLFile('post.tmpl.html',poems[0])


def load_poem(poem_id):
    poems = [
        {   
            'post_title':'post 1',
            'post_date':'9/22/14',
            'post_content':'This is the first line,<br/>it doesn\'t exactly rhyme.<br/>Just deal with it.</br>end'
        },
        {
            'post_title':'post 2',
            'post_date':'9/21/14',
            'post_content':'A second poem is just masochism'
        },
        {
            'post_title':'post 1',
            'post_date':'9/20/14',
            'post_content':'This is the next <i>poem</i>'
        }
    ]
    return ''.join(renderFromHTMLFile('post.tmpl.html',poem) for poem in poems)




class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(load_index())

class AjaxHandler(tornado.web.RequestHandler):
    def get(self):
        pass

    def post(self):
        pass


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
            (r'/', IndexHandler)

        ], debug=options.local
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()



