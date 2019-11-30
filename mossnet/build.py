#! /usr/bin/env python
from bs4 import BeautifulSoup
from re import search
from sys import stderr
from urllib.request import urlopen

def serialize_moss_results(moss_results_links, verbose=False):
    '''Serialize MOSS results into a 2D dictionary

    Args:
        ``moss_results_links`` (``list``): A list of MOSS result URLs

    Returns:
        ``dict``: A 2D dictionary ``D[student1][student2][filename] = (percent, student1 HTML, student2 HTML)``
    '''
    if isinstance(moss_results_links, str):
        urls = [l.strip() for l in open(moss_results_links.strip()).read().strip().splitlines()]
    else:
        urls = [l.strip() for l in moss_results_links]
    links = dict()
    for url_num,url in enumerate(urls):
        if verbose:
            stderr.write("Parsing MOSS report %d of %d...\r" % (url_num+1, len(urls)))
        bs = BeautifulSoup(urlopen(url).read().decode(), "lxml")
        curr_filename = None
        for row in bs.findAll('tr'):
            cols = row.findAll('td')
            if len(cols) != 3:
                continue
            try:
                moss_url = cols[0].find_all('a', href=True)[0]['href']
            except:
                stderr.write("Failed to parse row: %s" % row); continue
            if curr_filename is None:
                curr_filename = cols[0].find_all('a', href=True)[0].text.split('/')[-1].split()[0].strip()
            try:
                match_percent = int(cols[0].find_all('a', href=True)[0].text.split('/')[-1].split()[-1][1:-2])
            except:
                raise ValueError("Unable to parse as integer: %s" % cols[0].find_all('a', href=True)[0].text.split('/')[-1].split()[-1][1:-2])
            email1,email2 = [cols[i].find_all('a', href=True)[0].text.split('/')[-2] for i in [0,1]]
            if email1 not in links:
                links[email1] = dict()
            if email2 not in links[email1]:
                links[email1][email2] = dict()
            if email2 not in links:
                links[email2] = dict()
            if email1 not in links[email2]:
                links[email2][email1] = dict()
            if curr_filename is None:
                raise ValueError("Failed to parse filename from results URL: %s" % url)
            if curr_filename in links[email1][email2] or curr_filename in links[email2][email1]:
                raise ValueError("File '%s' found for (%s, %s) multiple times" % (curr_filename, email1, email2))
            moss_url_base = '/'.join(moss_url.rstrip('/').split('/')[:-1])
            main_html = urlopen(moss_url).read().decode()
            if email1 not in main_html or email2 not in main_html:
                raise RuntimeError("Didn't find the right email addresses in the match URL: %s" % moss_url)
            left_url = '%s/%s' % (moss_url_base, main_html.split('<FRAME SRC=')[2].split(' ')[0].replace('"',''))
            right_url = '%s/%s' % (moss_url_base, main_html.split('<FRAME SRC=')[3].split(' ')[0].replace('"',''))
            left_html = urlopen(left_url).read().decode().split("<HR>")[1].split("</BODY>")[0].split("<PRE>")[1].split("</PRE>")[0].strip()
            right_html = urlopen(right_url).read().decode().split("<HR>")[1].split("</BODY>")[0].split("<PRE>")[1].split("</PRE>")[0].strip()
            links[email1][email2][curr_filename] = (match_percent, left_html, right_html)
            links[email2][email1][curr_filename] = (match_percent, right_html, left_html)
    return links
