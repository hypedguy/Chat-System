import euclid
from utility import furtherPoint, projectvector
import random
import math

class Light:
    def __init__(self, position=euclid.Point3(0.,0.,0.), size=1.):
        self.position = position # a Point3
        self.size = size

class Collidable:
    def __init__(self, color=(255,255,0), roughness=1.0, transparency=0.0, refractionIndex=1.0):
        self.color = tuple(color)
        self.roughness = roughness
        self.transparencyIndex = transparency # 1=perfectly transparent
        self.refractionIndex = refractionIndex # min 1, max 2.5
    
    def getColor(self, coords=None):
        return self.color

    def getTransparency(self):
        return self.transparencyIndex

    def getReflectionIndex(self):
        return (1.0 - self.transparencyIndex) * (1 - self.roughness)

    # a perfectly rough object  (1.0) is perfectly diffuse
    # a perfectly smooth object (0.0) is perfectly reflective
    def getRoughness(self):
        return (1.0 - self.transparencyIndex) * self.roughness

    def getRefractionIndex(self):
        return self.refractionIndex

    def intersect(self, ray):
        raise BaseException("Must overload intersect() in class " + type(self).__name__)

    def normal(self, point):
        raise BaseException("Must overload normal() in class " +  type(self).__name__)

    def distance(self, ray):
        raise BaseException("Must overload distance() in class " + type(self).__name__)
        
    def __eq__(self, other):
        raise BaseException("Must overload __eq__() in class " + type(self).__name__)
        
    def __ne__(self, other):
        raise BaseException("Must overload __ne__() in class " + type(self).__name__)

class CollidableSphere(Collidable):
    def __init__(self, position=euclid.Point3(0.,0.,0.), color=(255,255,0), radius=1.,
                    roughness=1.0, transparency=0.0, refractionIndex=1.0):
        super().__init__(color=color, roughness=roughness,
                         transparency=transparency, refractionIndex=refractionIndex)
        self.position = position
        self.radius = radius
        self.shape = euclid.Sphere(self.position, self.radius)

    def getColor(self, coords=None):
        return self.color

    def intersect(self, ray):
        if abs(ray.v) == 0:
            return None
        return self.shape.intersect(ray)

    def distance(self, ray):
        return self.shape.distance(ray)

    def normal(self, point):
        return point - self.position

    def __repr__(self):
        x,y,z = self.position.xyz
        return "CollidableSphere(C<%.2f,%.2f,%.2f> r=%.2f)" % (x, y, z, self.radius)

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        A = self.position == other.position
        B = self.radius == other.radius
        return A and B

    def __ne__(self, other):
        return not self.__eq__(other)

class CollidablePlane(Collidable):
    def __init__(self, origin=euclid.Point3(0.,0.,0.), squaresize=4
                    ,normal=euclid.Vector3(0.,0.,1.),
                    roughness=1.0, transparency=0.0, refractionIndex=1.0):
        super().__init__(color=(255,255,255), roughness=roughness,
                     transparency=transparency, refractionIndex=refractionIndex)
        self.shape = euclid.Plane(origin, normal)
        normal = normal.normalized()
        self.squaresize = squaresize
        # let's find the unit vectors
        ux = euclid.Vector3(0., 1., 0.)
        uy = euclid.Vector3(0., 0., 1.)
        un = euclid.Vector3(1., 0., 0.) # 'original' normal
        # rotation axis
        axis = un.cross(normal)
        # cos(angle) between normal and unit normal
        angle = normal.dot(un)
        angle = math.acos(angle)
        rotation = euclid.Quaternion.new_rotate_axis(angle, axis)
        self.unitx = rotation * ux
        self.unity = rotation * uy

    def getColor(self, coords=None):
        if coords==None:
            return self.color
        # get plane x and y coordinates
        x = projectvector(coords, self.unitx).y
        y = projectvector(coords, self.unity).z
        x /= self.squaresize
        # y /= self.squaresize
        x = math.floor(x)
        y = math.floor(y)
        # if x % 2 == 0:
        #     if y % 2 == 0:

        if (x+y) % 2 == 0:
            return (0,0,0)
        return (255,255,255)

    def intersect(self, ray):
        return self.shape.intersect(ray)

    def distance(self, ray):
        return self.shape.distance(ray)

    def normal(self, point):
        line = self.shape.connect(point)
        otherpoint = furtherPoint(line, point)
        v = point - otherpoint
        if v.dot(self.shape.n) > 0:
            return self.shape.n.copy()
        return -1 * self.shape.n.copy()


    def __repr__(self):
        return "CollidablePlane"

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        A = self.shape == other.shape
        return A

    def __ne__(self, other):
        return not self.__eq__(other)

if __name__=='__main__':
    thing = CollidablePlane()
    vector = euclid.Vector3(5.,11.,3.)
    thing.getColor(vector)