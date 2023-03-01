#!/usr/bin/python
# This Python file uses the following encoding: utf-8

import sys
import re
import tempfile
import requests
from collections import namedtuple
from bs4 import BeautifulSoup


BLOGSPOT = re.compile(".*blogspot\.com*")
WORDPRESS = re.compile(".*wordpress\.com*")

# A cache of url to path for temporary css files
CSS_CACHE = {}

Stylesheet = namedtuple("Stylesheet", "url id media")

def get_page_text(post_url):
    try:
        r = requests.get(post_url)
    except Exception as e:
        print("Couldn't get content of {}.\n**Error**: {}".format(post_url, e))
    return r.text

def bundle_css(stylesheets):
    custom_css_tags = []
    try:
        for stylesheet in stylesheets:
            style_tag = []
            if stylesheet.url not in CSS_CACHE:
                r = requests.get(stylesheet.url)
                temp = tempfile.NamedTemporaryFile(delete=False)
                temp.write(r.text.encode('utf8'))
                temp.close()
                CSS_CACHE[stylesheet.url] = temp.name
            custom_attributes = ''
            if stylesheet.id != None:
                custom_attributes += ' id="{}"'.format(stylesheet.id)
            if stylesheet.media != None:
                custom_attributes += ' media="{}"'.format(stylesheet.media)
            css_file = open(CSS_CACHE[stylesheet.url], 'r')
            custom_css_tags.append('<style type="text/css"' + custom_attributes + '>' + css_file.read() + '</style>')
            css_file.close()
    except Exception as e:
        print('**Error**: Bundling css from {}, {}'.format(stylesheets, e))
        
    return "\n".join(custom_css_tags)

def print_contents_of_post(post_url):
    page_text = get_page_text(post_url)
    soup = BeautifulSoup(page_text, 'html.parser')

    try:
        filename = "{}".format(soup.title.string) + ".html"
        f = open(filename, 'w')
        f.write("<!DOCTYPE html>\n")
        f.write("<meta charset=\"utf-8\"/>\n")
        f.write("{}\n".format(soup.style))

        # Bundle each stylesheet and in-line into their own style tag
        css_links = []
        for stylesheet in soup.find_all('link', rel="stylesheet"):
            try:
                css_links.append(Stylesheet(url=stylesheet['href'], id=stylesheet['id'], media=stylesheet['media']))
            except:
                # workaround for stylesheets without id / media tags
                css_links.append(Stylesheet(url=stylesheet['href'], id=None, media=None))
        f.write("{}".format(bundle_css(css_links)))
        
        # Add a little more custom styling for padding
        f.write("<style>\ndiv {\n  padding-left: 100px;\n  padding-right: 100px;\n}\n</style>")
        f.write("<div id=\"main\" class=\"one-sidebar\">")
        f.write("<div id=\"content\" class=\"site-content\">")

        # Mapping for domain name of the site to the tag that wraps the content of the post we are interested in
        # The content of a single WP post on a page of a WP post is wrapped in the <article>...</article>
        # While the blogspot content is wrapped in <div class="post-body entry-content>...</div>
        if re.search(BLOGSPOT, post_url) != None:
            for i in soup.find_all('div', "post-body entry-content"):
                f.write("{}".format(i))
        elif re.search(WORDPRESS, post_url) != None:
            f.write("{}".format(soup.article))

        f.write("</div>\n</div>\n")
        f.write("</html>")
        f.close()
    except Exception as e:
        print("**Error**: Could not write to {}. Error: {}".format(filename, e))

if __name__  == "__main__":
    f = open("sample_article_links.txt", "r")
    for link in f:
        try:
            print_contents_of_post(link.strip())
        except Exception as e:
            print("**Error**: Unable to print contents of {}. Error: {}".format(link, e))
    f.close()
