#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Create web2py online book file by retreiving contents from its site
'''

import urllib
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

    def set_title(self, title):
        self.__title = title

    def append(self, content):
        self.__content += content

    def add_image(self, url):
        self.__images.append(url)

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
                data = data.replace('-lt-', '<').\
                        replace('-gt-', '>').\
                        replace('-nbsp-', ' ').\
                        replace('-amp-', '&').\
                        replace('-quot-', '"')
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
            if tag == 'p':
                self.__article.append('\n')
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
        elif self.__levels == 0:
            self.__consumer = None

    def handle_startendtag(self, tag, attrs):
        if self.__levels > 0:
            if tag == 'br':
                self.__consumer('\n')
            elif tag == 'img':
                for attr, value in attrs:
                    if attr == 'src':
                        self.__article.append('\n**image** %s\n' % value)
                        self.__article.add_image(value)
                        break

    def handle_data(self, data):
        if self.__consumer:
            self.__consumer(data)

    def handle_entityref(self, name):
        pass

    def handle_charref(self, name):
        pass

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

if __name__ == '__main__':
    main()
