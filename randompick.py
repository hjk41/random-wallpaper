# Random Windows Wallpapers from National Geographics 
# 
# This script obtains a randomly picked picture from National Geographics 
# website and set it as wallpaper on Windows. You need python install on 
# Windows to use it.
#
# This is Free software, use it at your own risk.
#
# Any comments or suggestions, drop me a mail: chuntao.hong@gmail.com

import time
import urllib.request
from datetime import datetime
from datetime import date
import random
import os
from html.parser import HTMLParser
import sys
import subprocess
import socks
import socket
import re

import json

import logging
import logging.handlers as handlers

def setup_logger(level=logging.INFO):
    '''
    Setup root logger so we can easily use it
    Params:
        level:  string  logging level
    '''
    logging.root.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(asctime)s] %(name)s-%(levelname)s: %(message)s')
    handler = handlers.RotatingFileHandler('log.txt', maxBytes=16384, backupCount=1)
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)

def setup_proxy():
    socks.set_default_proxy(socks.SOCKS5, "localhost")
    socket.socket = socks.socksocket
    def getaddrinfo(*args):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
    socket.getaddrinfo = getaddrinfo

class RandomWallPaper:
    def __init__(self):
        self.base_url = 'https://www.bing.com/images/async?q=wallpaper&first={}&count=30&qft=+filterui:imagesize-wallpaper'
        self.urlopenheader = { 'User-Agent' : 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        self.blacklist = set()
        with open('blacklist.txt', 'r') as f:
            self.blacklist = set([line.strip() for line in f.readlines()])

    def get_file(self):
        for i in range(0,3):
            try:
                first = random.randint(0,2000);
                logging.info("Rand value: {}".format(first))
                request_url = self.base_url.format(first)
                req = urllib.request.Request(request_url, None, headers=self.urlopenheader)
                response = urllib.request.urlopen(req, timeout=10)
                html_bytes = response.read()
                html = html_bytes.decode('utf-8')
                matches = re.findall('(m="{.*?purl&quot;:&quot;)(.*?)(&quot;.*?murl&quot;:&quot;)(.*?)(&quot;.*?)}',html)
                links = [m[3] for m in matches]
                pages = [m[1] for m in matches]
                if not links:
                    if i == 2:
                        logging.warn('failed to get any image, stopping...')
                        break
                    logging.warn('{} got no link, trying ...'.format(i))
                    continue
                print("Got {} links".format(len(links)))
                logging.info("Got {} links".format(len(links)))
                photoUrl = ""
                pageUrl = ""
                idx = 0
                while (idx < len(links)):
                    photoUrl = links[idx]
                    pageUrl = pages[idx]
                    ok = True
                    for black in self.blacklist:
                        if photoUrl.startswith(black):
                            ok = False
                            break
                    if ok:
                        break
                    idx = idx + 1
                # now, download the picture
                print("Downloading picture {}".format(photoUrl))
                req = urllib.request.Request(photoUrl, None, headers=self.urlopenheader)
                data = urllib.request.urlopen(req, timeout=30).read()
                if (len(data) < 50 * 1024):
                    continue
                filename = "__randompic.jpg"
                open(filename, "wb").write(data)
                logging.info("%s get photo: %s"%(str(datetime.now()), photoUrl))
                logging.info("page: {}".format(pageUrl))
                return filename
            except Exception as e:
                logging.info("Unexpected error: {}".format(str(e)))
    
    def set_wallpaper(self):
        file = self.get_file()
        if not file:
            return
        currentPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        cmd = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\SetWallPaper.exe'
        sinfo = subprocess.STARTUPINFO()
        sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen([cmd, '__randompic.jpg', 'fit'], startupinfo = sinfo)
        try:
            result = p.wait(10)
            if result != 0:
                logging.info("failed to set wallpaper")
        except:
            logging.info('Failed to set wallpaper in 10 seconds, killing it');
            p.kill();
    
class DivHrefRetriver(HTMLParser):
    """ Retrieve all the href contained in <div class='divClass'><a href='HREF'/></div>
    """
    allHrefs = []
    inDivTag = False
    divClass = ''
    def __init__(self, divClass):
        HTMLParser.__init__(self)
        self.divClass = divClass
        self.allHrefs = []
        self.inDivTag = False
    def handle_starttag(self, tag, attrs):        
        if (tag == 'div'):
            for attr in attrs:
                if (attr[0] == 'class' and attr[1] == self.divClass):
                    self.inDivTag = True
                    break
        elif (self.inDivTag and tag == 'a'):
            for attr in attrs:
                if (attr[0] == 'href'):
                    if (attr[1].find('?') != -1):
                        pass
                    self.allHrefs.append(attr[1])
                    #self.inDivTag = False
                    break
    def handle_endtag(self, tag):
        if (tag == 'div'):
            self.inDivTag = False

def GetPhotoUrls(html):
    """ 
        Parse html string and get all the photo urls
        html: a string representing the html
        returns: list of all the photo urls
    """
    photoInfo = DivHrefRetriver('photo_info')
    photoInfo.feed(html)
    return photoInfo.allHrefs

def GetPhotoUrl(html):
    """ 
        Get the url of the wallpaper given html of photo page
        html: string representing the photo page
        returns: string of actual photo url, or None if download fails
    """
    photoInfo = DivHrefRetriver('download_link')
    photoInfo.feed(html)
    if len(photoInfo.allHrefs) > 0:
        return photoInfo.allHrefs[0]
    else:
        return None

if __name__ == "__main__":
    setup_logger()
    # use proxy
    setup_proxy()
    potd = RandomWallPaper()
    potd.set_wallpaper()
