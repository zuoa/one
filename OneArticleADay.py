# -*- coding: utf-8 -*-
import feedparser
import torndb
from datetime import datetime
from time import mktime

def strip_tags(html):
    """
    Python strip html tags
    >>> str_text=strip_tags("<font color=red>hello</font>")
    >>> print str_text
    hello
    """
    from HTMLParser import HTMLParser
    html = html.strip()
    html = html.strip("\n")
    result = []
    parser = HTMLParser()
    parser.handle_data = result.append
    parser.feed(html)
    parser.close()

    r = ''.join(result)
    if len(r) >= 2048:
        r = r[:2048]
    return r


KEY_WORD = u'【每日一博】'
class RssFeed(object):
    def __init__(self, feed_url):
        d = feedparser.parse(feed_url)
        self.feed_url = feed_url
        self.encoding = d.encoding
        self.entries = d.entries
        self.length = len(d.entries)
        self.keys = d.entries[0].keys()



db = torndb.Connection('127.0.0.1', 'yu', 'root', 'passwd')

feed_urls = ['http://coolshell.cn/feed', 'http://www.oschina.net/news/rss', 'http://feed.cnblogs.com/blog/picked/rss']
articles = []

for url in feed_urls:
    feeds = RssFeed(url)
    for i in range(0, feeds.length):
        feed = feeds.entries[i]

        if 'oschina' in url and feed.title.find(KEY_WORD) < 0:
            continue

        if feed.title.find(KEY_WORD) >= 0:
            feed.title = feed.title.replace(KEY_WORD, '')
        dt = datetime.fromtimestamp(mktime(feed.published_parsed))
        articles.append((feed.title, feed.link, strip_tags(feed.summary), dt.strftime("%Y-%m-%d %H:%M:%S")))
    print url, ' articles size:', feeds.length

db.executemany('INSERT INTO one_article_a_day (title, url, summary, publish_time) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title),summary=VALUES(summary),publish_time=VALUES(publish_time);', articles)
print 'update db end'



try:
    with open("/tmp/one.update.time", "w") as update_file:
        update_time = datetime.now().strftime("%c")
        print "update time :", update_time
        update_file.write(update_time)
        update_file.close()
except:
    pass
