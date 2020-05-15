html = """<!doctype html>
<title>extract javascript object as json</title>
<script>
// ..
window.blog.data = {"activity":{"type":"read"}};
// ..
</script>
<p>some other html here
"""
import json
import re
from bs4 import BeautifulSoup  # $ pip install beautifulsoup4
from slimit import ast  # $ pip install slimit
from slimit.parser import Parser as JavascriptParser
from slimit.visitors import nodevisitor

soup = BeautifulSoup(html, 'html.parser')
tree = JavascriptParser().parse(soup.script.string)
obj = next(node.right for node in nodevisitor.visit(tree)
           if (isinstance(node, ast.Assign) and
               node.left.to_ecma() == 'window.blog.data'))
# HACK: easy way to parse the javascript object literal
data = json.loads(obj.to_ecma())  # NOTE: json format may be slightly different
assert data['activity']['type'] == 'read'