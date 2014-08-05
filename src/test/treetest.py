import unittest
import os
import time
from geogigpy.tree import Tree
from geogigpy import geogig
from testrepo import testRepo

class GeogigTreeTest(unittest.TestCase):
        
    repo = testRepo()

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        dst = self.getTempPath()
        return self.repo.clone(dst)  

    def testExportShp(self):
        repo = self.getClonedRepo()
        exportPath = os.path.join(os.path.dirname(__file__), "temp", str(time.time()) + ".shp").replace('\\', '/')    	
        tree = Tree(repo, geogig.HEAD, "parks")
        tree.exportshp(exportPath)
        self.assertTrue(os.path.exists(exportPath))

    def testFeatures(self):
        tree = Tree(self.repo, geogig.HEAD, "parks")
        features = tree.features
        self.assertEquals(5, len(features))
                
    def testFeatureType(self):
        tree = Tree(self.repo, geogig.HEAD, "parks")
        ftype = tree.featuretype
        self.assertEqual("DOUBLE", ftype["perimeter"])
        self.assertEqual("STRING", ftype["name"])
        self.assertEqual("MULTIPOLYGON", ftype["the_geom"])        
