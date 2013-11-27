import unittest
import os
from geogit.repo import Repository
import time
import shutil
from geogit.tree import Tree
import geogit

class GeogitTreeTest(unittest.TestCase):
        
    repo = Repository(os.path.join(os.path.dirname(__file__), 'data/testrepo'))

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        dst = self.getTempPath()
        return self.repo.clone(dst)  

    def testExportShp(self):
        repo = self.getClonedRepo()
        exportPath = os.path.join(os.path.dirname(__file__), "temp", str(time.time()) + ".shp").replace('\\', '/')    	
        tree = Tree(repo, geogit.HEAD, "parks")
        tree.exportshp(exportPath)
        self.assertTrue(os.path.exists(exportPath))

    def testFeatures(self):
        tree = Tree(self.repo, geogit.HEAD, "parks")
        features = tree.features()
        self.assertEquals(5, len(features))
