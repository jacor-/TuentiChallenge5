
'''
This problem is... pfff. The fucking hell in hearth.
'''


import time
import pycurl
import os,sys
import Image
import numpy
from pylab import *

'''
1) We need to generate valid antena code given a username and a password. 
To to this we read the prvided code in Forth and reproduce it in simple python.
'''
def generateCode(username, password):
    import numpy
    magic = 574381
    prev = numpy.sum([password]+map(ord, username)[::-1])
    return magic ^ prev
'''
2) Once we have the number, we need to send the request to the satellite. Which
returns a filename. We need to compute a 'checksum'. Reading the code again we
see what the fucking forth code is doing.
'''
def generate_code(s, code):
    count = [s.tm_year, s.tm_mon, s.tm_mday, s.tm_hour, s.tm_min, s.tm_sec, code]
    part_count = 30000
    for i in range(0, len(count)):
        part_count = part_count * 3 + count[i]
    return part_count

'''
3) If we ask the satellite for an image we will see a awful image... but for
different operators, we receive different images and we see something... a rare
square (not natural at all). Here happens the magic! We download a bunch of
noisy images from the satellite and let's aggregate them!
'''

def writeToFile(url):
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    with open(url.split("/")[-1], 'w') as f:
        c.setopt(c.WRITEFUNCTION, f.write)
        c.perform()

for usernum in range(100, 1000):    
    username = "operator%03d" %(usernum)
    password = "222222"
    sample_time = time.gmtime(time.mktime([2015,5,1,12+1,01,58,0,0,0]))
    antenacode = generateCode(username, int(password))
    s = sample_time
    filename = "%s_%s_%s_%s_%s_%s_%s_%s_%s_%s" % (username, password, antenacode, s.tm_year, s.tm_mon, s.tm_mday, s.tm_hour,    s.tm_min, s.tm_sec, 
    generate_code(sample_time, antenacode))
    writeToFile("http://54.83.207.93:14333/%s" % filename)

'''
4) Now we have a lot of images. Lets aggregate (clean) them.
'''
images =  []
for image in os.listdir("."):
    if "operator" in image:
        images.append(numpy.asarray(Image.open(image)))
images = numpy.array(images)

'''
4.1) They are greyscale, so the three RGB components must be the same. We compute
the mean over these three components and then, we compute the mean over the whole
set of images obtaining a clean image where we see a QR in the surface of the 
satellite!
'''
clean_image = numpy.mean(numpy.mean(images, axis=3),axis=0)

'''
4.1) Lets plot in the screen only the zone where we see the QR (and clean it to
make it perfectly visible). Once it is plot, take a picture with your smartphone
and write the result as the tuenti challenge solution!
'''
clean_image = 1. - numpy.round(clean_image / numpy.max(clean_image))
padding = 10
qr_image = clean_image[354-padding:403+padding,524-padding:573+padding]
imshow(qr_image, cmap = cm.Greys, interpolation = 'nearest')
