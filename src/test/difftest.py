import unittest
import os
import time
from testrepo import testRepo

class GeogigDiffTest(unittest.TestCase):
        
    repo = testRepo()

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        dst = self.getTempPath()
        return self.repo.clone(dst)  
    
    def testOldFeatureIsNone(self):
        diff = self.repo.log()[0].diff()[0]
        old = diff.oldobject()
        self.assertIsNotNone(old)       
        self.assertEquals("parks/5", old.path)
        attrs = old.attributes        
        self.assertEqual(15297.503295898438, attrs['area'])
        
    def testNewFeature(self): 
        diff = self.repo.log()[0].diff()[0]
        new = diff.newobject()
        self.assertIsNotNone(new)       
        self.assertEquals("parks/5", new.path)
        attrs = new.attributes
        self.assertEqual(15246.59765625, attrs['area'])
        
