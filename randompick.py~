import urllib2
from datetime import datetime
from datetime import date
from BeautifulSoup import BeautifulSoup
from PIL import Image
from win32con import *
from ctypes import windll
import random

class RandomWallPaper:
	def __init__(self, wide_scale=1.5):
		self.base_url = "http://photography.nationalgeographic.com/photography/photo-of-the-day/archive/?page="
		self.wide_scale = wide_scale

	def get_file(self):
		retry = True
		while (retry):
			# randomly choose a page
			page_num = random.randrange(1,29)
			collection_page_url = self.base_url + str(page_num)
			page = urllib2.urlopen(collection_page_url)
			soup = BeautifulSoup(page)
			s = soup('div', {'class': 'photo_info'})
			if(len(s)==0):
				continue
			# we now have a collection of photos, randomly pick one
			pic_num = random.randrange(0,len(s))
			hyper_link = s[pic_num].findAll('a')
			if(len(hyper_link)!=1):
				continue
			photo_page_url = 'http://photography.nationalgeographic.com' + hyper_link[0]['href']
			page = urllib2.urlopen(photo_page_url)
			soup = BeautifulSoup(page)
			s = soup('div', {'class': 'download_link'})
			link = None
			if len(s) > 0:
				link = s[0].contents[0]['href']
			else:
				continue
			# now, download the picture
			data = urllib2.urlopen(link).read()
			filename = "photos\\randompic"
			open(filename, "wb").write(data)
			# convert to BMP
			image = Image.open(filename)
			BMPPath = "photos\\randompick.bmp"
			image.save(BMPPath, "BMP")
			return BMPPath 
	
	def set_wallpaper(self):
		file = self.get_file()
		if not file:
			return
		result = windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, file, SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE)
		if not result:
			print("failed to set wallpaper")
	
if __name__ == "__main__":
	potd = RandomWallPaper()
	potd.set_wallpaper()
