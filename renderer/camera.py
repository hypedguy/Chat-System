import euclid
from euclid import Vector3, Point3

class Camera:
    def __init__(self, screenDim=(4,4), imageDim=(64,64), 
                 translation=euclid.Point3(0.,0.,0.), rotation=euclid.Quaternion(),
                 focallength=1.0):
        self.translation = translation
        self.rotation = rotation
        self.focallength = focallength # distance from camera to screen
        # Screen width is the real-world width/height of the screen
        self.screenw = screenDim[0]
        self.screenh = screenDim[1]
        # Image width is the number of pixels in the screen
        self.imagew = imageDim[0]
        self.imageh = imageDim[1]

    def generateRays(self, startline=0, endline=None): 
        """ 
            generate all the rays for the pixels in the screen.
            each ray starts from the camera's position and goes through the screen.

            The camera is originally at 0,0,0; and the screen originally is at
            A(f, .5w, .5h);
            B(f, .5w, -.5h);
            C(f, -.5w, -.5h);
            D(f, -.5w, .5h);

            Apply the transformation matrix for rotation to easily get the 
            actual screen position! don't do complex math if somebody already 
            did it for you
        """
        if not endline:
            endline = self.imageh
        A = Point3(self.focallength, 0.5*self.screenw, 0.5*self.screenh)
        B = Point3(self.focallength, 0.5*self.screenw, -0.5*self.screenh)
        # C = Point3(self.focallength, -0.5*self.screenw, -0.5*self.screenh)
        D = Point3(self.focallength, -0.5*self.screenw, 0.5*self.screenh)

        # rotate & translate the ABCD vectors
        A = self.rotation * A
        B = self.rotation * B
        D = self.rotation * D
        A += self.translation
        B += self.translation
        D += self.translation

        # unit vector for screen width, nx, is A to D divided by image width
        nx = D-A
        nx /= self.imagew
        # unit vector for screen height, ny, is A to B divided by image height
        ny = B-A
        ny /= self.imageh

        OA = A - self.translation # the first ray. will be modified to find the various rays
        for x in range(self.imagew):
            for y in range(startline, endline):
                # This is the initial ray for searching for collisions.
                vector = OA + (0.5 + x) * nx + (0.5 + y) * ny
                ray = euclid.Ray3(self.translation, vector)
                yield ray, x, y