# -*- coding: utf-8 -*-
import feedparser
import torndb
from datetime import datetime

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
    return ''.join(result)


KEY_WORD = u'【每日一博】'
class RssFeed(object):
    def __init__(self, feed_url):
        d = feedparser.parse(feed_url)
        self.feed_url = feed_url
        self.encoding = d.encoding
        self.entries = d.entries
        self.length = len(d.entries)
        self.keys = d.entries[0].keys()


articles = []
feeds = RssFeed('http://www.oschina.net/news/rss')


db = torndb.Connection('127.0.0.1', 'yu', 'root', 'ljd563538')
for i in reversed(range(0, feeds.length)):
    feed = feeds.entries[i]

    if feed.title.find(KEY_WORD) >= 0:
        feed.title = feed.title.replace(KEY_WORD, '')
        articles.append((feed.title, feed.link, strip_tags(feed.summary)))
print 'articles size:', len(articles)
db.executemany('INSERT INTO one_article_a_day (title, url, summary) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title),summary=VALUES(summary);', articles)
print 'update db end'



with open("/tmp/one.update.time", "w") as update_file:
    update_time = datetime.now().strftime("%c")
    print "update time :", update_time
    update_file.write(update_time)
    update_file.close()

