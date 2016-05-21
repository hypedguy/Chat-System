import math
import euclid

def clamp(m, x, M):
    if x < m:
        return m
    if x > M:
        return M
    return m

def dist(lineseg, point):
    if isinstance(lineseg, euclid.Point3):
        return abs(point - lineseg)
    L1 = abs(point - lineseg.p1)
    L2 = abs(point - lineseg.p2)
    return L1 if L1 < L2 else L2 # find the closer of the 2 points

def lerp(color1, color2, t):
    r1,g1,b1 = color1
    r2,g2,b2 = color2
    R = (1.0-t)*r1 + t*r2
    G = (1.0-t)*g1 + t*g2
    B = (1.0-t)*b1 + t*b2
    return (R,G,B)

def colorMultiply(rgb, n):
    r = rgb[0] * n
    g = rgb[1] * n
    b = rgb[1] * n
    return (r,g,b)

def colorSum(colors):
    R = G = B = 0.0
    for color in colors:
        R += color[0]
        G += color[1]
        B += color[2]
    return (R,G,B)

def colorFloor(color):
    r = int(color[0])
    g = int(color[1])
    b = int(color[2])
    return (r,g,b)

def weighedAverage(colors, weights):
    multcolors = []
    for i in range(len(colors)):
        multcolors.append(colorMultiply(colors[i], weights[i]))
    return colorFloor(colorSum(multcolors))


def floor(color):
    return (int(color[0]), int(color[1]), int(color[2]))

def closerPoint(lineseg, point):
    if isinstance(lineseg, euclid.Point3):
        return lineseg
    L1 = abs(point - lineseg.p1)
    L2 = abs(point - lineseg.p2)
    return lineseg.p1 if L1 < L2 else lineseg.p2 # find the closer of the 2 points

def furtherPoint(lineseg, point):
    if isinstance(lineseg, euclid.Point3):
        return lineseg
    L1 = abs(point - lineseg.p1)
    L2 = abs(point - lineseg.p2)
    return lineseg.p1 if L1 > L2 else lineseg.p2 # find the closer of the 2 points

# project v1 to v2
def projectvector(v1, v2, normalized=False):
    if not normalized:
        v2 = v2.normalized()
    scalar = v1.dot(v2)
    return scalar * v2