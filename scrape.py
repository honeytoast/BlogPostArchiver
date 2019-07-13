#!/usr/bin/python
# This Python file uses the following encoding: utf-8

import requests
import re
import sys
from collections import namedtuple
from bs4 import BeautifulSoup


BLOGSPOT = re.compile(".*blogspot\.com*")
WORDPRESS = re.compile(".*wordpress\.com*")

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
            r = requests.get(stylesheet.url)
            custom_attributes = ''
            if stylesheet.id != None:
                custom_attributes += ' id="{}"'.format(stylesheet.id)
            if stylesheet.media != None:
                custom_attributes += ' media="{}"'.format(stylesheet.media)
            custom_css_tags.append('<style type="text/css"' + custom_attributes + '>' + r.text + '</style>')
    except Exception as e:
        print('**Error**: Bundling css from {}, {}'.format(stylesheets, e))
    return "\n".join(custom_css_tags)

def print_contents_of_post(post_url):
    page_text = get_page_text(post_url)
    soup = BeautifulSoup(page_text, 'html.parser')

    try:
        filename = soup.title.string.encode('utf8') + ".html"
        f = open(filename, 'w')
        f.write('<!DOCTYPE html>\n')
        f.write('<meta charset="utf-8"/>\n')
        f.write("{}\n".format(soup.style.encode('utf8')))

        # Bundle each stylesheet and in-line into their own style tag
        css_links = []
        for stylesheet in soup.find_all('link', rel="stylesheet"):
            css_links.append(Stylesheet(url=stylesheet['href'], id=stylesheet['id'], media=stylesheet['media']))
        f.write(bundle_css(css_links).encode('utf8'))

        # Add a little more custom styling for padding
        f.write('<style>\ndiv {\n  padding-left: 100px;\n  padding-right: 100px;\n}\n</style>')
        f.write('<div id="main" class="one-sidebar">')
        f.write('<div id="content" class="site-content">')

        # Mapping for domain name of the site to the tag that wraps the content of the post we are interested in
        # The content of a single WP post on a page of a WP post is wrapped in the <article>...</article>
        # While the blogspot content is wrapped in <div class="post-body entry-content>...</div>
        if re.search(BLOGSPOT, post_url) != None:
            for i in soup.find_all('div', "post-body entry-content"):
                f.write(i.encode('utf8'))
        elif re.search(WORDPRESS, post_url) != None:
            f.write(soup.article.encode('utf8'))

        f.write('</div>\n</div>\n')
        f.write('</html>')
        f.close()
    except Exception as e:
        print("**Error**: Could not write to {}. Error: {}".format(filename, e))

if __name__  == '__main__':
    f = open('7122019.txt', 'r')
    for link in f:
        try:
            print_contents_of_post(link.strip())
        except Exception as e:
            print("**Error**: Unable to print contents of {}. Error: {}".format(link, e))
    f.close()
