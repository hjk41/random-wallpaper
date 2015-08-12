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

class RandomWallPaper:
    def __init__(self):
        self.index_page_url = "http://photography.nationalgeographic.com/photography/photo-of-the-day/archive/?page="
        self.base_url = 'http://photography.nationalgeographic.com'

    def get_file(self):
        retry = True
        while (retry):
            try:
                # randomly choose a page
                page_num = random.randrange(1,68)
                collection_page_url = self.index_page_url + str(page_num)
                page = urllib.request.urlopen(collection_page_url)
                photoPages = GetPhotoUrls(page.read().decode())
                if(len(photoPages) == 0):
                    continue
                # we now have a collection of photos, randomly pick one
                pic_num = random.randrange(0,len(photoPages))
                hyper_link = photoPages[pic_num]
                # now parse the photo page and download photo
                photo_page_url = ''
                if (hyper_link.startswith("http")):
                    photo_page_url = hyper_link
                else:
                    photo_page_url = self.base_url + hyper_link
                print("[photo_page] ", photo_page_url)
                page = urllib.request.urlopen(photo_page_url)
                photoUrl = GetPhotoUrl(page.read().decode())
                print("[photo] ", photoUrl)
                if photoUrl is None:
                    continue
                if (not photoUrl.endswith(".jpg")):
                    continue
                if (photoUrl.startswith("//")):
                    photoUrl = "http:" + photoUrl
                # now, download the picture
                data = urllib.request.urlopen(photoUrl).read()
                filename = "__randompic.jpg"
                open(filename, "wb").write(data)
                print("%s get photo: %s"%(str(datetime.now()), photoUrl))
                return filename
            except:
                print("Unexpected error:", sys.exc_info())
    
    def set_wallpaper(self):
        file = self.get_file()
        if not file:
            return
        currentPath = os.path.dirname(os.path.realpath(sys.argv[0]))
        cmd = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\SetWallPaper.exe'
        p = subprocess.Popen([cmd, '__randompic.jpg'])
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
    potd = RandomWallPaper()
    potd.set_wallpaper()
