#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Create web2py online book file by retreiving contents from its site
'''

import urllib
import os
from HTMLParser import HTMLParser

class WebArticle(object):
    def __init__(self):
        self.__title = ''
        self.__content = ''
        self.__images = []

    def title(self):
        return self.__title

    def content(self):
        return self.__content

    def images(self):
        return self.__images

    def set_title(self, title):
        self.__title = title

    def append(self, content):
        self.__content += content

    def append_image(self, url):
        self.__images.append(url)

    def polish(self):
        self.__content = self.__content.\
                replace('-lt-', '<').\
                replace('-gt-', '>').\
                replace('-nbsp-', ' ').\
                replace('-amp-', '&').\
                replace('-quot-', '"')

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
        self.__article = WebArticle()
        self.__consumer = None
        self.__url = url
        self.__levels = 0

    def article(self):
        return self.__article if self.__article.title() and self.__article.content() else None

    def handle_starttag(self, tag, attrs):
        if self.__levels == 0:
            if tag == 'div':
                for attr, value in attrs:
                    if attr == 'class' and value == 'article':
                        self.__consumer = self.__article.append
                        self.__levels = 1
            # If the title is still emtpy, then try to get it
            elif tag == 'a' and not self.__article.title():
                href, url = attrs[0]
                if self.__url.endswith(url):
                    self.__consumer = self.__article.set_title
        elif self.__levels > 0:
            self.__levels = self.__levels + 1
            if tag in ('p', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'code'):
                self.__article.append('\n')
            elif tag == 'div':
                for attr, value in attrs:
                    # This is for index only, we don't need it
                    if attr == 'class' and value == 'inxx':
                        self.__consumer = None
                        self.__last_consumer = self.__consumer
            elif tag == 'table':
                self.__consumer = WebDocParser.CodeTable()
            elif tag == 'tr':
                self.__consumer.create_row()
            elif tag == 'td':
                self.__consumer.create_column()

    def handle_endtag(self, tag):
        if self.__levels > 0:
            self.__levels = self.__levels - 1
            if tag == 'table':
                self.__article.append('\n')
                self.__article.append(self.__consumer.content())
                self.__article.append('\n')
                self.__consumer = self.__article.append
            elif tag in ('li'):
                self.__article.append('\n')
            elif tag == 'div' and not self.__consumer:
                if hasattr(self, '__last_consumer') and self.__last_consumer:
                    self.__consumer = self.__last_consumer
                    del self.__last_consumer
        elif self.__levels == 0:
            self.__consumer = None

    def handle_startendtag(self, tag, attrs):
        if self.__levels > 0:
            if tag == 'br':
                self.__consumer('\n')
            elif tag == 'img':
                for attr, value in attrs:
                    if attr == 'src':
                        if not value.startswith('http'):
                            value = 'http://web2py.com' + value
                        self.__article.append('<img %s>' % value)
                        self.__article.append_image(value)
                        break

    def handle_data(self, data):
        if self.__consumer:
            self.__consumer(data)

    def handle_entityref(self, name):
        pass

    def handle_charref(self, name):
        pass

    def feed(self, html):
        super(WebDocParser, self).feed(html)
        self.__article.polish()

    def close(self):
        super(WebDocParser, self).close()

def article_from(url):
    opener = urllib.urlopen(url)
    html = opener.read()
    # The parser will eliminate these special tags from the stream
    # Then they won't be output
    # We replace them with another special string, then later when parsed
    # They will be replaced by real characters
    html = html.replace('&lt;', '-lt-').\
            replace('&gt;', '-gt-').\
            replace('&nbsp;', '-nbsp-').\
            replace('&amp;', '-amp-').\
            replace('&quot;', '-quot-')
    parser = WebDocParser(url)
    parser.feed(html)
    return parser.article()

def fetch_images(article):
    images = []
    seq = 0
    for url in article.images():
        print 'Fetching image from "' + url + '"...'
        opener = urllib.urlopen(url)
        data = opener.read()
        name = '%s' % seq
        seq = seq + 1
        images.append((data, name))
    return images

def main():
    articles = []
    base = 'http://web2py.com/books/default/chapter/29/%d'
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

        '''
        for article in articles:
            images = fetch_images(article)
            if images:
                folder = article.title().replace(' ', '')
                if not os.path.exists(folder):
                    os.mkdir(folder)
                for data, name in images:
                    print name, data
        '''

if __name__ == '__main__':
    main()
