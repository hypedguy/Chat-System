from scene import Scene
import objects
import euclid
from camera import Camera
import time
import sys

if __name__=="__main__":
    #import rpdb2; rpdb2.start_embedded_debugger('1234')
    # do raycaster things
    objectlist = [objects.CollidableSphere(position=euclid.Point3(10.,-5.,5.), radius=3.,
                     color=(255, 215, 0), roughness=0.8),
                  objects.CollidableSphere(position=euclid.Point3(6.,0.,0.), radius=1.,
                     color=(0, 255, 0), roughness=0.99),
                  objects.CollidableSphere(position=euclid.Point3(20.,5.,0.), radius=11.,
                     color=(188, 188, 177), roughness=0.8),
                  objects.CollidablePlane(origin=euclid.Point3(10.,0.,-10.)
                    ,normal=euclid.Vector3(.5, 0.,-1.),
                    roughness=0.8)]
    lights = [objects.Light(position=euclid.Point3(0.,0.,0.)),
    objects.Light(position=euclid.Point3(10.,0.,5.)),
    objects.Light(position=euclid.Point3(-50.,0.,55.))]
    try:
        i,j = sys.argv[1].split(",")
        i,j = int(i), int(j)
    except:
        i,j = 256, 256
    camera = Camera(imageDim=(i,j),focallength=3., screenDim=(16,9))
    myScene = Scene(camera=camera, objects=objectlist, lights=lights)
    myScene.skycolor = (90, 90, 255)
    starttime = time.clock()
    myScene.render(depth=3)
    endtime = time.clock()
    print("Took %.2f seconds for rendering a %dx%d image." % (endtime - starttime,
        camera.imagew, camera.imageh))