# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 17:38:02 2015

@author: virgiltataru
"""

import PIL
from PIL import Image
import numpy, json
 #encoding
def encrypt(img):
     #return str(''.join(str(list(img.getdata()))))
     return json.dumps(numpy.array(img).tolist())   
        
 #decoding
def decrypt(d):
     d = numpy.array(json.loads(d))
     return PIL.Image.fromarray(numpy.uint8(d))
if __name__=='__main__':
    img = Image.open('r.png')
    pixels = img.load()
    d = encrypt(img)
    print(type(d))
    decrypt(d).show()
    
