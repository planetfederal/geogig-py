import unittest
import os
from geogit.repo import Repository
import time
import shutil
import geogit
from geogit.feature import Feature
from shapely.geometry import Polygon

class GeogitFeatureTest(unittest.TestCase):
        
    repo = Repository(os.path.join(os.path.dirname(__file__), 'data/testrepo'))

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        src = self.repo.url
        dst = self.getTempPath()
        shutil.copytree(src, dst)
        return Repository(dst)

    def testExists(self):
        feature = Feature(self.repo, geogit.HEAD, "parks/1")                    
        self.assertTrue(feature.exists())
        feature = Feature(self.repo, geogit.HEAD, "wrong/path")                    
        self.assertFalse(feature.exists())

    def testAttributes(self):    	
    	feature = Feature(self.repo, geogit.HEAD, "parks/1")    	            
        data = feature.attributes()
        self.assertEquals(8, len(data))
        self.assertEquals("Public", data["usage"])
        self.assertTrue("owner" in data)
        self.assertTrue("agency" in data)
        self.assertTrue("name" in data)
        self.assertTrue("parktype" in data)
        self.assertTrue("area" in data)
        self.assertTrue("perimeter" in data)  
        self.assertTrue("the_geom" in data)  
        self.assertTrue(isinstance(data["the_geom"][0], Polygon))        
        
    def testDiff(self):
        feature = Feature(self.repo, geogit.HEAD, "parks/5")
        featureB = Feature(self.repo, geogit.HEAD + "~1", "parks/5")
        diffs = feature.diff(featureB)        
        self.assertTrue(2, len(diffs))
        areas = diffs["area"]
        self.assertEquals("15297.503295898438", areas[1])
        self.assertEquals("15246.59765625", areas[0])
        self.assertTrue("the_geom" in diffs)

    def testBlame(self):
        feature = Feature(self.repo, geogit.HEAD, "parks/5")
        blame = feature.blame()        
        self.assertEquals(8, len(blame))
        attrs = feature.attributes()
        for k,v in blame.iteritems():
            self.assertTrue(v[0], attrs[k])

    def testFeatureType(self):
        feature = Feature(self.repo, geogit.HEAD, "parks/5")
        ftype = feature.featuretype()

