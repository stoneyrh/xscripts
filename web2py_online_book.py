#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Create web2py online book file by retreiving contents from its site
'''

import urllib
from HTMLParser import HTMLParser

class WebArticle(object):
    def __init__(self):
        self.title = ""
        self.content = ""

    def set_title(self, title):
        self.title = title

    def append(self, content):
        self.content += content

class WebDocParser(HTMLParser, object):
    def __init__(self, url):
        super(WebDocParser, self).__init__()
        self.article_ = WebArticle()
        self.consumer_ = None
        self.url_ = url
        self.levels_ = 0

    def article(self):
        return self.article_ if self.article_.title and self.article_.content else None

    def handle_starttag(self, tag, attrs):
        # If the title is still emtpy, then try to get it
        if not self.article_.title and tag == 'a':
            href, url = attrs[0]
            if self.url_.endswith(url):
                self.consumer_ = self.article_.set_title
        if self.levels_ == 0 and tag == 'div':
            for attr, value in attrs:
                if attr == 'class' and value == 'article':
                    self.consumer_ = self.article_.append
                    self.levels_ = 1
        if self.levels_ > 0:
            self.levels_ = self.levels_ + 1
            if tag == 'p':
                self.article_.append("\n")

    def handle_endtag(self, tag):
        if self.levels_ > 0:
            self.levels_ = self.levels_ - 1
        if self.levels_ == 0:
            self.consumer_ = None

    def handle_startendtag(self, tag, attrs):
        if self.levels_ > 0:
            if tag == 'br':
                self.article_.append("\n")
            elif tag == 'img':
                for attr, value in attrs:
                    if attr == 'src':
                        self.article_.append("\n**image** %s\n" % value)
                        break

    def handle_data(self, data):
        if self.consumer_:
            self.consumer_(data)

    def handle_entityref(self, name):
        pass

    def handle_charref(self, name):
        pass

def article_from(url):
    opener = urllib.urlopen(url)
    html = opener.read()
    parser = WebDocParser(url)
    parser.feed(html)
    return parser.article()

def main():
    articles = []
    base = "http://web2py.com/books/default/chapter/29/%d"
    for chapter in range(15):
        url = base % chapter
        print 'Retrieving ' + url
        article = article_from(url)
        if article:
            articles.append(article)
    if articles:
        book = open('web2py_online_book.txt', 'w')
        for article in articles:
            book.write("\n".join([article.title, article.content]))
        book.close()

if __name__ == '__main__':
    main()
