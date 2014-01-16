import os
import sys
from geogitpy.cliconnector import CLIConnector
from geogitpy.py4jconnector import shutdownServer

libpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(libpath)        

import time
from geogitpy.repo import Repository
import unittest
from geogitpy import geogit
from repotest import GeogitRepositoryTest
from treetest import GeogitTreeTest
from featuretest import GeogitFeatureTest
from commitishtest import GeogitCommitishTest

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
    shutdownServer()
               
        
def suite():
    suite = unittest.makeSuite(GeogitTreeTest, 'test')    
    suite.addTests(unittest.makeSuite(GeogitRepositoryTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogitFeatureTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogitCommitishTest, 'test'))
    #suite = unittest.makeSuite(GeogitTempTest, 'test')
    return suite
   

if __name__ == '__main__': 
    runner=unittest.TextTestRunner()
    runner.run(suite())
    shutdownServer()
