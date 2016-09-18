# Random Windows Wallpapers from National Geographics 
# 
# This script obtains a randomly picked picture from National Geographics 
# website and set it as wallpaper on Windows. You need python install on 
# Windows to use it.
#
# This is Free software, use it at your own risk.
#
# Any comments or suggestions, drop me a mail: chuntao.hong@gmail.com


import urllib.request
from datetime import datetime
from datetime import date
import random
import os
from html.parser import HTMLParser
import sys
import subprocess
import re

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
    handler = handlers.TimedRotatingFileHandler('log.txt', backupCount=100)
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)

class RandomWallPaper:
    def __init__(self):
        self.base_url = 'http://cn.bing.com/images/search?q=national+geographic&qft=+filterui:imagesize-custom_1920_1080+filterui:aspect-wide'
        self.urlopenheader = { 'User-Agent' : 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0'}

    def get_file(self):
        for i in range(1,10):
            try:
                # randomly choose a page
                first = random.randrange(1, 1000)
                collection_page_url = self.base_url + '&first=' + str(first)
                req = urllib.request.Request(collection_page_url, None, headers=self.urlopenheader)
                resp = urllib.request.urlopen(req)
                html = resp.read().decode()                
                links = re.findall('imgurl:&quot;(.*?)&quot;',html)
                pages = re.findall('surl:&quot;(.*?)&quot;',html)
                idx = random.randrange(1, len(links))
                photoUrl = links[idx]
                photoPage = pages[idx]
                # now, download the picture
                req = urllib.request.Request(photoUrl, None, headers=self.urlopenheader)
                data = urllib.request.urlopen(req).read()
                filename = "__randompic.jpg"
                open(filename, "wb").write(data)
                print("%s get photo: %s"%(str(datetime.now()), photoUrl))
                logging.info('Photo page: {}'.format(photoPage))
                return filename
            except:
                print("Unexpected error:", sys.exc_info())
    
    def set_wallpaper(self):
        file = self.get_file()
        if not file:
            return
        currentPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        cmd = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\SetWallPaper.exe'
        sinfo = subprocess.STARTUPINFO()
        sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen([cmd, '__randompic.jpg'], startupinfo = sinfo)
        result = p.wait()
        if result != 0:
            print("failed to set wallpaper")
    
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
    potd = RandomWallPaper()
    potd.set_wallpaper()
