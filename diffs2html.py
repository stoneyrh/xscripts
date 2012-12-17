from diff2html import diff2html
import os

ignoreList = []

def readIgnoreList():
    try:
        file = open(os.path.join(os.path.dirname(__file__), '.diffignore'), 'rt')
        lines = file.readlines()
        file.close()
    except:
        pass

def isIgnore(name):
    global ignoreList
    if not ignoreList:
        readIgnoreList()
        # TODO: Check if name in ignore list
        return True
    return False

def parseFileName(line):
    line = line[11:]
    pos = len(line) / 2
    aname = line[2:pos]
    #bname = line[pos + 3:]
    return aname

def parseRevision(line):
    revision = line[6:].split()[0]
    return revision

def diffs2html(diff):
    '''
    Return a list of dictionary, each of item has the following fields:
    name     - the file name of this diff
    revision - blob SHA1 of this diff
    html     - diff representation in HTML
    '''
    htmls = []
    lines = diff.split('\n')
    diffLineNumbers = []
    currentLine = 0
    while currentLine < len(lines):
        line = lines[currentLine]
        if line.lower().startswith('diff --git'):
            diffLineNumbers.append(currentLine)
        currentLine = currentLine + 1
    if diffLineNumbers:
        diffLineNumbers.append(-1)
        diffLineNumbers.reverse()
        start = diffLineNumbers.pop()
        while len(diffLineNumbers) > 0:
            end = diffLineNumbers.pop()
            diffLine = lines[start]
            name = parseFileName(diffLine)
            # Ignore those ignored files
            if not isIgnore(name):
                diffLines = lines[start:end]
                if diffLines:
                    revision = '<UNKNOWN>'
                    for line in diffLines:
                        if line.startswith('index'):
                            revision = parseRevision(line)
                            break
                    html = diff2html('\n'.join(diffLines))
                    if html:
                        htmls.append({'name':name, 'revision':revision, 'html':html})
            start = end
    return htmls

def main():
    import sys
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
        htmls = []
        for filename in filenames:
            file = open(filename, 'rt')
            diff = file.read()
            file.close()
            html = diffs2html(diff)
            if html:
                htmls.extend(html)
        if htmls:
            for html in htmls:
                print '<h3>' + html['name'] + '[' + html['revision'] + ']' + '</h3><br/>' + html['html']
    else:
        print 'Usage: parsediff.py file [file...]'

if __name__ == '__main__':
    main()
