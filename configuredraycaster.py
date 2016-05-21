from scene import Scene
import objects
import euclid
from camera import Camera
import time
import sys
import json

def parseconfig(config):
    data = json.loads(config)
    objectlist, lights = [], []
    for conf in data["objects"]:
        if conf["type"] == "sphere":
            posx, posy, posz = conf["position"]
            r = conf["radius"]
            col = conf["color"]
            roughness = conf["roughness"]
            obj = objects.CollidableSphere(position=euclid.Point3(posx, posy, posz), radius=r,
                         color=col, roughness=roughness)
        elif conf["type"] == "plane":
            orix, oriy, oriz = conf["origin"]
            normx, normy, normz = conf["normal"]
            roughness = conf["roughness"]
            obj = objects.CollidablePlane(origin=euclid.Point3(orix, oriy, oriz)
                    ,normal=euclid.Vector3(normx, normy, normz),
                    roughness=roughness)
        objectlist.append(obj)
    for conf in data["lights"]:
        x, y, z = conf
        lights.append(objects.Light(position=euclid.Point3(x, y, z)))
    conf = data["camera"]
    imgw, imgh = conf["imageDim"]
    scrw, scrh = conf["screenDim"]
    focal = conf["focallength"]
    camera = Camera(imageDim=(imgw, imgh),focallength=focal, screenDim=(scrw, scrh))
    scene = Scene(camera = camera, objects=objectlist, lights=lights)
    scene.skycolor = tuple(data["skycolor"])
    depth = data["depth"]

    return camera, depth, lights, objectlist, scene

# returns Image object if filename is None
def dorender(config, filename=None, start=0, end=None):
    camera, depth, lights, objectlist, myScene = parseconfig(config)

    depth = 2

    # do raycaster things
    starttime = time.clock()
    if filename:
        myScene.render(depth=depth, start=start, end=end, tofile=True, filename=filename)
    else:
        result = myScene.render(depth=depth, start=start, end=end, tofile=False)
    if not end:
        end = camera.imageh
    height = end - start
    endtime = time.clock()
    comment = ("Took %.2f seconds for rendering a %dx%d image." % (endtime - starttime,
        camera.imagew, height))
    try:
        return comment, result
    except:
        return comment


if __name__=="__main__":
    with open("config2.json") as f:
        config = f.read()
    dorender(config, filename="test.png")