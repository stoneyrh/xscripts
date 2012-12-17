"""
Script for convert unified diff text into html
"""

import re

separator = '*' * 3
def handleBlock(block):
    """
    Turn a block of lines into a list like this
    - Line 1
    + Line 2
           -> [("Line 1", "Line 2")]
    - Line 1
    - Line 2
           -> [("Line 1", ""), ("Line 2", "")]
    + Line 1
    + Line 2
           -> [("Line 1", ""), ("Line 2", "")]
    - Line 1
    + Line 2
    + Line 3
           -> [("Line 1", "Line 2"), ("", "Line 3")]
    - Line 1
    - Line 2
    + Line 3
           -> [("Line 1", "Line 3"), ("Line 2", "")]
    """
    mlines = filter(lambda line : line.startswith('-'), block)
    plines = filter(lambda line : line.startswith('+'), block)
    mcount = len(mlines)
    pcount = len(plines)
    if mcount > pcount:
        plines.extend([''] * (mcount - pcount))
    elif pcount > mcount:
        mlines.extend([''] * (pcount - mcount))
    count = max(mcount, pcount)
    return [(mlines[i],plines[i]) for i in range(count)]

def adjust(lines):
    newLines = []
    for line in lines:
        if not line.startswith('\\ No newline at end of file'):
            newLines.append(line)
    return newLines

def makeBlocks(diff):
    blocks = []
    if len(diff) <= 0:
        return
    pattern = re.compile('(\d+)')
    lines = diff.split('\n')
    lines = adjust(lines)
    num = 0
    total = len(lines)
    while num < total:
        line = lines[num]
        if line.startswith('---') or line.startswith('+++') or \
               line.startswith('===') or line.lower().startswith('index') or \
               line.lower().startswith('diff'):
            num = num + 1
            continue
        if line.startswith('@@'):
            # Retrieve the line number
            numbers = pattern.findall(line)
            if len(numbers) != 4:
                # TODO: Wrong numbers?
                pass
            numbers = map(lambda n : int(n), numbers)
            leftLine = numbers[0]
            rightLine = numbers[2]
            num = num + 1
            if len(blocks) > 0:
                blocks.append((separator, separator, separator, separator));
            while num < total:
                line = lines[num]
                # Leave this line to outside loop
                if line.startswith('@@') or line.lower().startswith('index') or line.startswith('diff'):
                    break
                # The lines after this line will make a block
                if line.startswith('-') or line.startswith('+'):
                    # Find the next line not start with '-' or '+'
                    block = [line]
                    num = num + 1
                    while num < total:
                        line = lines[num]
                        if line.startswith('-') or line.startswith('+'):
                            block.append(line)
                            num = num + 1
                        else:
                            # When breaking out, line save the current line
                            # This line should be appended to blocks
                            break
                    block = handleBlock(block)
                    for left, right in block:
                        if left and right:
                            blocks.append((str(leftLine), left, str(rightLine), right))
                            leftLine = leftLine + 1
                            rightLine = rightLine + 1
                        elif left:
                            blocks.append((str(leftLine), left, '', right))
                            leftLine = leftLine + 1
                        else:
                            blocks.append(('', left, str(rightLine), right))
                            rightLine = rightLine + 1
                # end if
                if num < total:
                    blocks.append((str(leftLine), line, str(rightLine), line))
                    leftLine = leftLine + 1
                    rightLine = rightLine + 1
                    num = num + 1
        else: # line.startswith('@@')
            num = num + 1
    return blocks

bg_table = '#eeeeee'
table = '<table style="width:100%%;text-align=left;background:' + bg_table + '#eeeeee;padding:0;margin:0;border:1px;cellspacing:0;">\n%s\n</table>'
row   = '<tr><td style="width:2%%;color:red;text-align:center;">%s</td><td style="width:48%%;color:%s;background:%s;">%s</td><td style="width:2%%;color:red;text-align:center;">%s</td><td style="width:48%%;color:%s;background:%s;">%s</td></tr>'
empty_row = '<tr style="background:purple;"><td style="text-align:center;"><hr/></td><td style="text-align:center;"><hr/></td><td style="text-align:center;"><hr/></td><td style="text-align:center;"><hr/></td></tr>'

color_nor = 'black'
color_mod = 'black'
color_add = 'black'
color_del = 'black'
bg_mod    = 'orange'
bg_add    = '#00FF80'
bg_del    = 'red'

def text2html(plain):
    html = plain.replace('<', '&lt;').\
                 replace('>', '&gt;').\
                 replace('\n', '<br/>').\
                 replace('\t', '    ').\
                 replace(' ', '&nbsp;')
    return html

def makeHTML(blocks):
    # blocks is None
    if not blocks:
        return
    rows = []
    for block in blocks:
        # TODO: Encode block data
        leftLine, left, rightLine, right = block
        if leftLine.startswith(separator):
            rows.append(empty_row)
            continue
        color_left = color_right = color_nor
        bg_left = bg_right = bg_table
        if left.startswith('-'):
            if right.startswith('+'):
                color_left  = color_mod
                color_right = color_add
                bg_left     = bg_mod
                bg_right    = bg_add
            else:
                color_left  = color_mod
                color_right = color_del
                bg_left     = bg_mod
                bg_right    = bg_del
        else:
            if right.startswith('+'):
                color_right = color_add
                bg_right    = bg_add
                bg_left     = bg_mod
        # Remove the first -/+
        if left.startswith('-'):
            left = left[1:]
        if right.startswith('+'):
            right = right[1:]
        rows.append(row % (leftLine, color_left, bg_left, text2html(left), rightLine, color_right, bg_right, text2html(right)))
    return table % '\n\t'.join(rows)

def diff2html(diff):
    blocks = makeBlocks(diff)
    html   = makeHTML(blocks)
    return html

def main():
    diff = """--- a/xcommon/unit_tests/xbyte_array_tests.cpp
+++ b/xcommon/unit_tests/xbyte_array_tests.cpp
@@ -208,3 +208,14 @@ TEST(xbyte_array_tests, test_function_replace)
     ASSERT_TRUE(byte_array.replace(0, &_xi16, sizeof(_xi16)));
     ASSERT_EQ(byte_array.value_at<xint16_t>(0), _xi16);
 }
+
+TEST(xbyte_array_tests, test_function_clear)
+{
+    xbyte_array byte_array;
+    ASSERT_TRUE(byte_array.is_empty());
+    xint16_t xi16 = -16;
+    byte_array.append(xi16);
+    ASSERT_FALSE(byte_array.is_empty());
+    byte_array.clear();
+    ASSERT_TRUE(byte_array.is_empty());
+}
"""
    html = diff2html(diff)
    print html
    diff = """--- a/xcommon/xbyte_array.h
+++ b/xcommon/xbyte_array.h
@@ -112,6 +112,7 @@ class xbyte_array
         xsize_t capacity() const { return data_.capacity(); }
         void reserve(xsize_t space) { data_.reserve(space); }
         const xbyte_ptr data() const { return (const xbyte_ptr)(&data_[0]); }
+        void clear() { std::vector<xbyte> none; data_.swap(none); }

         xbyte_array& operator += (const xbyte_array& rhs);
         xbyte_array operator + (const xbyte_array& rhs) const;
"""
    html = diff2html(diff)
    print html

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]
        htmls = []
        for filename in filenames:
            file = open(filename, 'rt')
            diff = file.read()
            file.close()
            html = diff2html(diff)
            htmls.append(html)
        if htmls:
            print '\n'.join(htmls)
    else:
        print 'Usage: diff2html.py file [file...]'
        #print 'The following is an output example.'
        #print '-' * 80
        #main()
