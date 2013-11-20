import os
import sys

libpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(libpath)        

import time
from geogit.repo import Repository
import unittest
import geogit
from repotest import GeogitRepositoryTest
from treetest import GeogitTreeTest
from featuretest import GeogitFeatureTest

def getTempRepoPath():
    return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')


def createRepo():
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
    repo.createbranch(geogit.HEAD, "mybranch")
    path = os.path.join(os.path.dirname(__file__), "data", "shp", "4", "parks.shp")
    repo.importshp(path)
    repo.addandcommit("message_4")
    repo.checkout("mybranch")
    path = os.path.join(os.path.dirname(__file__), "data", "shp", "5", "parks.shp")
    repo.importshp(path)
    repo.addandcommit("message_5")
        

def suite():
    suite = unittest.makeSuite(GeogitTreeTest, 'test')
    suite = unittest.makeSuite(GeogitRepositoryTest, 'test')
    suite = unittest.makeSuite(GeogitFeatureTest, 'test')
    return suite
   

if __name__ == '__main__':     
    runner=unittest.TextTestRunner()
    runner.run(suite())