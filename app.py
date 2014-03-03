from tornado import web, ioloop, httpserver
import torndb
import os

from config import  *

class Application(web.Application):
    def __init__(self):
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "template"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = False,
            cookie_secret = "8B12CB2EEF49B4431EE27D1654060710",
            login_url = "/login",
            debug=True,
            autoescape = None
        )

        handlers = [
            (r"/post", PostHandler),
            (r"/go/([0-9]+)", JumpHandler),
            (r"/([0-9]*)", PageHandler),
        ]

        web.Application.__init__(self, handlers, **settings)

class PostHandler(web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.db = torndb.Connection(DB_IP, DB_NAME, DB_USER, DB_PASSWD)
        super(PostHandler, self).__init__(application, request, **kwargs)

    def __del__(self):
        self.db.close()
    def get(self):
        self.render("post.html")

    def post(self):
        title = self.get_argument('title')
        url = self.get_argument('url')
        summary = self.get_argument('summary')

        if title and url:
            self.db.execute('INSERT INTO one_article_a_day (title, url, summary) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title),summary=VALUES(summary);', title, url, summary)

class PageHandler(web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.db = torndb.Connection(DB_IP, DB_NAME, DB_USER, DB_PASSWD)
        super(PageHandler, self).__init__(application, request, **kwargs)

    def __del__(self):
        self.db.close()

    def get(self, page):
        if not page:
            page = 0
        articles = self.db.query('SELECT * FROM one_article_a_day ORDER BY id DESC LIMIT %s, 50;', int(page) * 50)

        update_time = ""
        try:
            with open("/tmp/one.update.time", "r") as update_file:
                update_time = update_file.readline()
                update_file.close()
        except:
            pass
            
        self.render("weekly.html", articles=articles, update_time=update_time)

class JumpHandler(web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.db = torndb.Connection(DB_IP, DB_NAME, DB_USER, DB_PASSWD)
        super(JumpHandler, self).__init__(application, request, **kwargs)

    def __del__(self):
        self.db.close()

    def get(self, pid):
        articles = self.db.query('SELECT * FROM one_article_a_day WHERE id=%s;', pid)
        if (not articles) or (0 == len(articles)):
            self.redirect("/")
            return
        self.db.execute("UPDATE one_article_a_day SET clicks=clicks+1 WHERE id=%s;", pid)
        self.redirect(articles[0].get('url'))

if __name__ == "__main__":
    http_server = httpserver.HTTPServer(Application())
    http_server.listen(8888)
    print 'start server on', 8888
    ioloop.IOLoop.instance().start()