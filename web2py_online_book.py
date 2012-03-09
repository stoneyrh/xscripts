#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Create web2py online book file by retreiving contents from its site
'''

import urllib
from HTMLParser import HTMLParser

class WebArticle(object):
    def __init__(self):
        self.title_ = ""
        self.content_ = ""
        self.images_ = []

    def title(self):
        return self.title_

    def content(self):
        return self.content_

    def set_title(self, title):
        self.title_ = title

    def append(self, content):
        self.content_ += content

    def add_image(self, url):
        self.images_.append(url)

class WebDocParser(HTMLParser, object):
    #
    class CodeTable(object):
        def __init__(self):
            self.rows = []

        def create_row(self):
            self.rows.append([])

        def create_column(self):
            row = self.rows[-1]
            row.append([])

        def __call__(self, data):
            row = self.rows[-1]
            if data != '\n':
                if len(row[-1]) == 0:
                    row[-1].append('')
                row[-1][-1] += data
            else:
                row[-1].append('')

        def content(self):
            c = [] 
            for row in self.rows:
                columns = len(row)
                lines = len(row[0])
                # Check if all columns have the same number of lines
                for column in range(columns):
                    if len(row[column]) < lines:
                        rest = lines - len(row[column])
                        row[column].extend([''] * rest)
                b = []
                for line in range(lines):
                    l = []
                    for column in range(columns):
                        # In case if a cell without content
                        if len(row[column]) == 0:
                            l.append('')
                        else:
                            l.append(row[column][line])
                    b.append(' '.join(l))
                c.append('\n'.join(b))
            return '\n'.join(c)
    #
    def __init__(self, url):
        super(WebDocParser, self).__init__()
        self.article_ = WebArticle()
        self.consumer_ = None
        self.url_ = url
        self.levels_ = 0

    def article(self):
        return self.article_ if self.article_.title() and self.article_.content() else None

    def handle_starttag(self, tag, attrs):
        if self.levels_ == 0:
            if tag == 'div':
                for attr, value in attrs:
                    if attr == 'class' and value == 'article':
                        self.consumer_ = self.article_.append
                        self.levels_ = 1
            # If the title is still emtpy, then try to get it
            elif tag == 'a' and not self.article_.title():
                href, url = attrs[0]
                if self.url_.endswith(url):
                    self.consumer_ = self.article_.set_title
        elif self.levels_ > 0:
            self.levels_ = self.levels_ + 1
            if tag == 'p':
                self.article_.append("\n")
            elif tag == 'table':
                self.consumer_ = WebDocParser.CodeTable()
            elif tag == 'tr':
                self.consumer_.create_row()
            elif tag == 'td':
                self.consumer_.create_column()

    def handle_endtag(self, tag):
        if self.levels_ > 0:
            self.levels_ = self.levels_ - 1
            if tag == 'table':
                self.article_.append('\n')
                self.article_.append(self.consumer_.content())
                self.article_.append('\n')
                self.consumer_ = self.article_.append
        elif self.levels_ == 0:
            self.consumer_ = None

    def handle_startendtag(self, tag, attrs):
        if self.levels_ > 0:
            if tag == 'br':
                self.consumer_("\n")
            elif tag == 'img':
                for attr, value in attrs:
                    if attr == 'src':
                        self.article_.append("\n**image** %s\n" % value)
                        self.article_.add_image(value)
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
            print ' ' * 10, article.title()
    if articles:
        headline = 'web2py online book'
        footline = 'vim:tw=78:fo=tcq2:isk=!-~,^*,^\|,^\":ts=8:ft=help:norl:'
        index = '\n'.join(['|' + article.title().replace(' ', '-') + '|' for article in articles])
        book = open('web2py_online_book.txt', 'w')
        book.write(headline)
        book.write('\n')
        book.write('\n')
        book.write(index)
        for article in articles:
            book.write('\n'.join(['*' + article.title().replace(' ', '-') + '*', article.content()]))
        book.write('\n')
        book.write(footline)
        book.close()

if __name__ == '__main__':
    main()
