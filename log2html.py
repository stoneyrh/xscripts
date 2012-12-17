from diffs2html import diffs2html
import os

def log2html(log):
    '''
    Return a list of dictionary, each dictionary has the following fields:
    commit - the commit SHA1 for this commit
    author - the author making this commit
    date   - the datetime making this commit
    diffs  - a list of dictionary, each of dictionary has the following fields:
             name     - file name of this diff
             revision - blob SHA1 of this diff
             html     - diff representation in HTML
    '''
    lines = log.split('\n')
    currentLine = 0
    totalLines = len(lines)
    htmls = []
    while currentLine < totalLines:
        line = lines[currentLine]
        if line.startswith('commit '):
            commit = line[7:]
            author = lines[currentLine + 1][8:]
            date = lines[currentLine + 2][8:]
            offset = 3
            while currentLine + offset < totalLines:
                line = lines[currentLine + offset]
                if line.startswith('diff --git'):
                    break
                offset = offset + 1
            message = '\n'.join(lines[currentLine + 3:currentLine + offset])
            diffOffset = offset
            while currentLine + offset < totalLines:
                line = lines[currentLine + offset]
                if line.startswith('commit '):
                    break
                offset = offset + 1
            diffs = '\n'.join(lines[currentLine + diffOffset:currentLine + offset])
            diffshtml = diffs2html(diffs)
            if diffshtml:
                htmls.append({'commit':commit, 'author':author, 'date':date, 'message':message, 'diffs':diffshtml})
            currentLine = currentLine + offset
        else:
            currentLine = currentLine + 1
    return htmls

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
        htmls = []
        for filename in filenames:
            file = open(filename, 'rt')
            log = file.read()
            file.close()
            html = log2html(log)
            if html:
                htmls.extend(html)
        if htmls:
            for html in htmls:
                print '<h3> commit:' + html['commit'] + '</h3>'
                print '<h3> author:' + html['author'] + '</h3>'
                print '<h3> date:' + html['date'] + '</h3>'
                print '<h3> message:' + html['message'] + '</h3>'
                diffs = html['diffs']
                for diff in diffs:
                    print '<h3>' + diff['name'] + '[' + diff['revision'] + ']' + '</h3><br/>' + diff['html']
    else:
        print 'Usage: parsediff.py file [file...]'
