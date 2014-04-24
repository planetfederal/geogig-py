import unittest
import os
from geogitpy.repo import Repository
import time
import shutil
from geogitpy import geogit
from geogitpy.feature import Feature
from shapely.geometry import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from testrepo import testRepo

class GeogitFeatureTest(unittest.TestCase):
        
    repo = testRepo()

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
        data = feature.attributes    
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
        self.assertEquals(15297.503295898438, areas[1])
        self.assertEquals(15246.59765625, areas[0])
        self.assertTrue("the_geom" in diffs)

    def testBlame(self):
        feature = Feature(self.repo, geogit.HEAD, "parks/5")
        blame = feature.blame()        
        self.assertEquals(8, len(blame))
        attrs = feature.attributes
        for k,v in blame.iteritems():
            self.assertTrue(v[0], attrs[k])

    def testFeatureType(self):
        feature = Feature(self.repo, geogit.HEAD, "parks/5")
        ftype = feature.featuretype()
        self.assertTrue("owner" in ftype)
        self.assertTrue("agency" in ftype)
        self.assertTrue("name" in ftype)
        self.assertTrue("parktype" in ftype)
        self.assertTrue("area" in ftype)
        self.assertTrue("perimeter" in ftype)  
        self.assertTrue("the_geom" in ftype) 
        self.assertEquals("MULTIPOLYGON EPSG:4326", ftype['the_geom'])
        
    def testGeom(self):
        feature = Feature(self.repo, geogit.HEAD, "parks/5")
        geom = feature.geom
        self.assertTrue(isinstance(geom, MultiPolygon)) 
        
    def testGeomFieldName(self):
        feature = Feature(self.repo, geogit.HEAD, "parks/5")
        name = feature.geomfieldname
        self.assertEquals("the_geom", name)
        
    def testNoGeom(self):
        feature = Feature(self.repo, geogit.HEAD, "parks/5")
        allattrs = feature.attributes
        attrs = feature.attributesnogeom
        self.assertEquals(len(allattrs), len(attrs) + 1)
        self.assertTrue("owner" in attrs)
        self.assertTrue("agency" in attrs)
        self.assertTrue("name" in attrs)
        self.assertTrue("parktype" in attrs)
        self.assertTrue("area" in attrs)
        self.assertTrue("perimeter" in attrs)  
        self.assertFalse("the_geom" in attrs)     

