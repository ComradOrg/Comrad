#!/usr/bin/env python
import os
ROOT = os.path.dirname(__file__)
os.chdir(ROOT)
theme_fn=os.path.join(ROOT,'theme.html')
with open(theme_fn) as theme_f: theme=theme_f.read()

os.system('pandoc ../../README.md > content.html')
with open('content.html') as content_f,open('index.html','w') as of:
    content = content_f.read() #.replace('\n  * ','</li>\n<li>')
    content=content.replace('&lt;','<').replace('&gt;','>')
    total = theme.replace('[[CONTENT]]',content)
    of.write(total)
os.remove('content.html')
