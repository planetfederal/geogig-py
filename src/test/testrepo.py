from geogitpy.repo import Repository
import os
from geogitpy import geogit
from geogitpy.py4jconnector import shutdownServer
import time

_repo = None

def getTempRepoPath():
    return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

def createRepo():
    global _repo
    repo = Repository(getTempRepoPath(), init = True)
    path = os.path.join(os.path.dirname(__file__), "data", "shp", "1", "parks.shp")
    repo.importshp(path)   
    repo.addandcommit("message")
    path = os.path.join(os.path.dirname(__file__), "data", "shp", "2", "parks.shp")
    repo.importshp(path)
    repo.addandcommit("message_2")        
    path = os.path.join(os.path.dirname(__file__), "data", "shp", "3", "parks.shp")
    repo.importshp(path)
    repo.addandcommit("message_3")
    repo.createbranch(geogit.HEAD, "conflicted")
    repo.createbranch(geogit.HEAD, "unconflicted")
    path = os.path.join(os.path.dirname(__file__), "data", "shp", "4", "parks.shp")
    repo.importshp(path)
    repo.addandcommit("message_4")
    repo.checkout("conflicted")
    path = os.path.join(os.path.dirname(__file__), "data", "shp", "5", "parks.shp")
    repo.importshp(path)
    repo.addandcommit("message_5")
    repo.checkout("unconflicted")
    path = os.path.join(os.path.dirname(__file__), "data", "shp", "6", "parks.shp")
    repo.importshp(path)
    repo.addandcommit("message_6")
    _repo = repo
    shutdownServer()
    
def testRepo():
    if _repo is None:
        createRepo()
    return _repo