#! /usr/bin/env python
from mossnet.MossNet import MossNet
from bs4 import BeautifulSoup
from re import search,sub
from sys import stderr
from urllib.request import urlopen
from warnings import warn

def build(moss_results_links, verbose=False):
    '''Download MOSS results into a ``MossNet`` object

    Args:
        ``moss_results_links`` (``list``): A list of MOSS result URLs

        ``verbose`` (``bool``): ``True`` to show verbose messages, otherwise ``False``

    Returns:
        ``MossNet``: A ``MossNet`` object
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
        curr_filename1 = None; curr_filename2 = None
        for row in bs.findAll('tr'):
            cols = row.findAll('td')
            if len(cols) != 3:
                continue
            try:
                moss_url = cols[0].find_all('a', href=True)[0]['href']
            except:
                stderr.write("Failed to parse row: %s" % row); continue
            curr_filename1,curr_filename2 = [cols[i].find_all('a', href=True)[0].text.split('/')[-1].split()[0].strip() for i in [0,1]]
            email1,email2 = [cols[i].find_all('a', href=True)[0].text.split('/')[-2] for i in [0,1]]
            if email1 == email2:
                continue # skip self-match
            if email1 not in links:
                links[email1] = dict()
            if email2 not in links[email1]:
                links[email1][email2] = dict()
            if email2 not in links:
                links[email2] = dict()
            if email1 not in links[email2]:
                links[email2][email1] = dict()
            if (curr_filename1,curr_filename2) in links[email1][email2] or (curr_filename2,curr_filename1) in links[email2][email1]:
                warn("Files '%s' and '%s' found for (%s, %s) multiple times. Taking latest version" % (curr_filename1, curr_filename2, email1, email2))
            moss_url_base = '/'.join(moss_url.rstrip('/').split('/')[:-1])
            main_html = urlopen(moss_url).read().decode()
            if email1 not in main_html or email2 not in main_html:
                raise RuntimeError("Didn't find the right email addresses in the match URL: %s" % moss_url)
            top_url = '%s/%s' % (moss_url_base, main_html.split('<FRAME SRC=')[1].split(' ')[0].replace('"',''))
            left_url = '%s/%s' % (moss_url_base, main_html.split('<FRAME SRC=')[2].split(' ')[0].replace('"',''))
            right_url = '%s/%s' % (moss_url_base, main_html.split('<FRAME SRC=')[3].split(' ')[0].replace('"',''))
            left_percent,right_percent = [int(part.split('(')[-1]) for part in urlopen(top_url).read().decode().split("%")[:2]]
            left_html = sub(r'<(A|/A).*?>', "", urlopen(left_url).read().decode().split("<HR>")[1].split("</BODY>")[0].split("<PRE>")[1].split("</PRE>")[0].strip())
            right_html = sub(r'<(A|/A).*?>', "", urlopen(right_url).read().decode().split("<HR>")[1].split("</BODY>")[0].split("<PRE>")[1].split("</PRE>")[0].strip())
            links[email1][email2][(curr_filename1,curr_filename2)] = ((left_percent, left_html), (right_percent, right_html))
            links[email2][email1][(curr_filename2,curr_filename1)] = ((right_percent, right_html), (left_percent, left_html))
    return MossNet(links)
