import camera
from PIL import Image
import euclid
import math
from utility import *
import os

class Scene:
    def __init__(self, camera=camera.Camera(), objects=[], lights=[]):
        self.camera = camera
        self.objects = objects
        self.lights = lights
        self.skycolor = (90, 90, 255)

    def findLightedColor(self, obj, point):
        truecolor = obj.getColor(point)

        # these two for highlights
        angles = []
        spectralAngles = []
        # this for brightness
        distances = []
        # this for intersection tests
        intersected = [] 

        # normal vector
        Vn = obj.normal(point).normalize()
        # line to viewer
        Vv = (point - self.camera.translation).normalize()

        # Try to draw a line to a light source
        for light in self.lights:
            ray = euclid.Ray3(point, light.position-point)
            canDoLight = True
            for thing in self.objects:
                inter = thing.intersect(ray)
                # if it's an intersection, no light!
                if isinstance(inter, euclid.Point3):
                    if inter:
                        if thing != obj:
                            canDoLight=False
                            intersected.append(True)
                else:
                    if inter and inter.length > 0.05:
                        if thing.getTransparency() > 0.0:
                            continue
                        else:
                            canDoLight = False
                            intersected.append(True)
                            break
            # spectral reflection stuff
            if canDoLight:
                intersected.append(False)

                N = obj.normal(point)
                N.normalize()
                dot = N.dot(ray.v.normalized())
                angles.append(dot)

                # find reflection vector & viewer vector angle
                Vl = (light.position - point)
                distances.append(len(Vl))
                Vl.normalize()
                # must rotate L around axis N x L, equal to angle.
                N_L_angle = math.acos(Vl.dot(N))
                axis = Vl.cross(N)
                rot = euclid.Quaternion.new_rotate_axis(N_L_angle*2, axis)
                Reflection = rot * Vl
                # get angle between viewer and reflection
                spectralAngles.append(Reflection.dot(Vv))

        shadowed = True
        for tf in intersected:
            shadowed &= tf

        if shadowed:
            return (0,0,0)
        
        angle = max(angles) # The greatest angle wins
        distance = min(distances) # smallest distance
        # but wait, there's more! Find the spectral lighting angle
        spectral = max(spectralAngles)
        # lighted color
        lightedcolor = truecolor #lerp((0,0,0), truecolor, 7 / distance**2)

        # If the material is more reflective, the highlight is smaller & more intense
        # but for now, if the angle is above a threshold make it white
        if spectral < -0.985:
            return lerp(lightedcolor, (255,255,255), abs((spectral+0.985)*100)**3)
        return lerp((0,0,0), lightedcolor, angle)

    def trace(self, ray, depth=0):
        hits = []
        for x in self.objects:
            inter = x.intersect(ray)
            if isinstance(inter, euclid.Point3):
                if inter:
                    hits.append((inter, x))
            else:
                if inter and inter.length > 0.05:
                    hits.append((inter,x))
        # Register the hit on the closest object
        if len(hits) > 0:
            origin       = ray.p
            closestObj   = None
            closestPoint = None
            closestDist  = None
            for x,obj in hits:
                if not closestPoint:
                    closestObj = obj
                    closestPoint = closerPoint(x, origin)
                    closestDist = dist(x, origin)
                else:
                    distance = dist(x, origin)
                    if distance < closestDist:
                        closestDist = distance
                        closestPoint = closerPoint(x, origin)
                        closestObj = obj

            # Dot the closest obj's normal and the ray. If positive, internal reflection,
            # at least in the case of a sphere.
            # With the closest object, get color or get secondary rays.
            diffuse = self.findLightedColor(closestObj, closestPoint)
            if depth <= 0:
                return diffuse
            # All secondary rays here
            # eg, reflection, refraction...
            # Sum up the colors, then return.

            """ Final color = (diffuseness + reflection) + refraction
                after all, diffuse colors are just really scattered reflections.
                transparent part is taken out first,
                then diffuse+reflection

            """
            reflected = (0,0,0)
            
            roughness    = closestObj.getRoughness()
            reflection   = closestObj.getReflectionIndex()
            
            normal = closestObj.normal(closestPoint)
            normal.normalize()

            # disabled because too much effort. perhaps return later.
            """if transparency > 0.0:
                # do refraction
                refractedray = self.refractRay(closestObj, closestPoint, normal, ray, depth)
                refracted_selfcolor = colorMultiply(diffuse, transparency)
                if not refractedray:
                    refracted = (255,255,0); #refracted_selfcolor
                else:
                    refracted = self.trace(refractedray, depth-1)
                refracted = weighedAverage([refracted, refracted_selfcolor],
                                           [transparency, 1-transparency])
                #...
                # sum colors, return true color"""
            if roughness < 1.0:
                ## do reflection
                #  rotate ray
                dotab = ray.v.dot(normal)
                rotatedray = ray.copy()
                rotatedray.v -= normal * dotab * 2
                rotatedray.p = closestPoint
                inter = closestObj.intersect(rotatedray)
                if inter:
                    direction = rotatedray.v.normalized()
                    if isinstance(inter, euclid.Point3):
                        rotatedray.p = (inter + normal*0.01)
                    else:
                        rotatedray.p += direction * inter.length
                # trace!
                reflected = self.trace(rotatedray, depth-1)

            return weighedAverage([diffuse, reflected], 
                                  [roughness, reflection])
        # hit nothing
        return self.skycolor

    # returns a ray, not a color
    def trace_internal(self, obj, ray, depth=0):
        if depth <= 0:
            return None
        # First, find the point of incidence
        inter = obj.intersect(ray)
        if not inter:
            return ray
        point = furtherPoint(inter, ray.p)
        # Next, reflect
        normal = -obj.normal(point)
        normal.normalized()
        dotab = ray.v.dot(normal)
        rotatedray = ray.copy()
        rotatedray.v -= normal * dotab * 2
        rotatedray.p = point
        # Find next point of incidence
        inter = obj.intersect(rotatedray)
        if not inter:
            return rotatedray
        point = furtherPoint(inter, ray.p)

        # Try to rotate from material to air again
        normal = obj.normal(ray.p)
        cross = normal.cross(ray.v)
        cross.normalize()
        n = obj.getRefractionIndex()
        try:
            angleOfIncidence = math.acos(normal.cross(cross).dot(rotatedray.v))
            rotateBy = math.asin(math.sin(angleOfIncidence) * n)
            quat = euclid.Quaternion.new_rotate_axis(rotateBy, cross)
            rotatedray = quat * rotatedray
            rotatedray.p = exit
            return rotatedray
        except ValueError:
            return self.trace_internal(obj, rotatedray, depth-1)



    def refractRay(self, obj, intersect, normal, ray, depth):
        normal.normalize()
        ray = ray.copy()
        ray.v.normalize()
        rotationAxis = normal.cross(ray.v)
        #angleOfIncidence = math.acos(normal.cross(rotationAxis).dot(ray.v)) 
        angleOfIncidence = math.acos(normal.dot(-ray.v))
        n = obj.getRefractionIndex()
        # first rotation is air to material.
        rotateBy = math.asin(math.sin(angleOfIncidence) / n)
        quat = euclid.Quaternion.new_rotate_axis(rotateBy, rotationAxis)
        ray = quat * ray
        ray.v.normalize()
        ray.p = intersect
        # Next, find the exit point.
        lineseg = obj.intersect(ray)
        exit = furtherPoint(lineseg, ray.p)
        ray.p = exit.copy()
        # Rotate again, material to air.
        normal = obj.normal(ray.p)
        rotationAxis = normal.cross(ray.v)
        rotationAxis.normalize()
        try:
            angleOfIncidence = math.acos(normal.dot(ray.v))
            rotateBy = math.asin(math.sin(angleOfIncidence) * n)
            quat = euclid.Quaternion.new_rotate_axis(rotateBy, rotationAxis)
            ray = quat * ray
            ray.p = exit
            return ray
        except ValueError:
            return None
            return self.trace_internal(obj, ray, depth-1)

        

    def render(self, depth=1, filename="out/test.png", start=0, end=None, tofile=True):
        # figure out the final image size
        if not end:
            end = self.camera.imageh
        height = end - start

        img = Image.new('RGB', 
            (self.camera.imagew, height), (0,0,255))
        pixels = img.load()
        for ray, x, y in self.camera.generateRays(start, end):
            color = self.trace(ray, depth)
            y -= start
            pixels[x,y] = floor(color)
        if tofile:
            directory = os.path.dirname(filename) # the directory path
            filename  = os.path.basename(filename) # the actual test.png part
            base      = "".join(filename.split(".")[:-1])
            outfile = ("{base}-img{camera.imagew}.{height}-"
                       "f{camera.focallength}-screen{camera.screenw}"
                       ".{camera.screenh}"
                       ".png").format(camera=self.camera, base=base, height=height)
            if directory:
                img.save(directory + "/" + outfile)
            else:
                img.save(outfile)
        else:
            return img