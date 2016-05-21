# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 17:38:02 2015

@author: virgiltataru
"""
table = ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']

def hex(i):
    first = table[i // 16]
    second = table[i % 16]
    return first + second

from PIL import Image
import base64
def tohex(rgb):
    code = ""
    for i in range(3):
        code += hex(rgb[i])
    return code

def torgb(hexcode):
    r = int(hexcode[:2], 16)
    g = int(hexcode[2:4], 16)
    b = int(hexcode[4:], 16)
    return (r,g,b)

def torgb_low(hexcode):
    r = int(hexcode[0]+'0', 16)
    g = int(hexcode[2]+'0', 16)
    b = int(hexcode[4]+'0', 16)
    return (r,g,b)

 #encoding
def encrypt(image):
    w, h = image.size
    out = []
    pixels = image.load()
    for y in range(h):
        out.append([])
        for x in range(w):
            out[-1].append(tohex(pixels[x,y]))
    out2 = []
    for row in out:
        out2.append(','.join(row))
    out = '\n'.join(out2)
    return out
#decoding
def decrypt(data, low=False):
    rows = data.split("\n")
    totalpixels = []
    for row in rows:
        hexcodes = row.split(',')
        pixels = []
        for code in hexcodes:
            if low:
                pixels.append(torgb_low(code))    
            else:
                pixels.append(torgb(code))
        totalpixels.append(pixels)
    h = len(totalpixels)
    w = len(totalpixels[1])
    img = Image.new('RGB', (w, h))
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            pixels[x, y] = totalpixels[y][x]
    return img

if __name__=='__main__':
    img = Image.open('0-img64.32-f3.0-screen8.8.png')
    data = encrypt(img)
    img = decrypt(data)
    img.show()
