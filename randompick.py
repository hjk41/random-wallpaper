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
import socks
import socket
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
    handler = handlers.TimedRotatingFileHandler('log.txt', backupCount=100)
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)

class RandomWallPaper:
    def __init__(self):
        #self.base_url = 'http://cn.bing.com/images/search?q=wallpaper+nature&qft=+filterui:imagesize-custom_1920_1080+filterui:aspect-wide'
        self.base_url = 'http://cn.bing.com/images/search?q=bing+wallpaper&qft=+filterui:imagesize-custom_1920_1080+filterui:aspect-wide'
        #self.base_url = 'http://cn.bing.com/images/search?q=national+geographic&qft=+filterui:imagesize-custom_1920_1080+filterui:aspect-wide'
        self.urlopenheader = { 'User-Agent' : 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0'}

    def get_file(self):
        for i in range(0,1):
            try:
                browser = webdriver.PhantomJS()
                browser.set_window_position(0,0)
                browser.get(self.base_url)
                for _ in range(10):
                    browser.execute_script("window.scrollBy(0,10000)")
                    try:
                        btn = browser.find_element_by_xpath('//a[@class="btn_seemore"]')
                        btn.click()
                    except:
                        pass
                print("Get to the end of the windows, now choosing one image at random")
                pics = browser.find_elements_by_xpath('//a[@class="iusc"]')
                links = []
                pages = []
                for p in pics:
                    js = json.loads(p.get_attribute('m'))
                    links.append(js["murl"])
                    pages.append(js["purl"])
                browser.quit()
                print("Got {} links".format(len(links)))
                idx = random.randrange(1, len(links))
                photoUrl = links[idx]
                photoPage = pages[idx]
                # now, download the picture
                print("Downloading picture {}".format(photoUrl))
                # use proxy
                #socks.set_default_proxy(socks.SOCKS5, "localhost")
                #socket.socket = socks.socksocket
                #def getaddrinfo(*args):
                #    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
                #socket.getaddrinfo = getaddrinfo

                req = urllib.request.Request(photoUrl, None, headers=self.urlopenheader)
                data = urllib.request.urlopen(req, timeout=30).read()
                if (len(data) < 50 * 1024):
                    continue
                filename = "__randompic.jpg"
                open(filename, "wb").write(data)
                logging.info("%s get photo: %s"%(str(datetime.now()), photoUrl))
                logging.info('Photo page: {}'.format(photoPage))
                return filename
            except:
                logging.info("Unexpected error:", sys.exc_info())
                browser.quit()
    
    def set_wallpaper(self):
        file = self.get_file()
        if not file:
            return
        currentPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        cmd = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\SetWallPaper.exe'
        sinfo = subprocess.STARTUPINFO()
        sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen([cmd, '__randompic.jpg'], startupinfo = sinfo)
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
    #socks.set_default_proxy(socks.SOCKS5, "localhost")
    #socket.socket = socks.socksocket
    #def getaddrinfo(*args):
    #    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
    #socket.getaddrinfo = getaddrinfo
    setup_logger()
    potd = RandomWallPaper()
    potd.set_wallpaper()
