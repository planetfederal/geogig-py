import unittest
import os
from geogit.repo import Repository
import time
import shutil

class GeogitTreeTest(unittest.TestCase):
        
    repo = Repository(os.path.join(os.path.dirname(__file__), 'data/testrepo'))

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        src = self.repo.url
        dst = self.getTempPath()
        shutil.copytree(src, dst)
        return Repository(dst)

    def testExportShp(self):
    	exportPath = os.path.join(self.getTempPath(), "export.shp")
    	tree = Tree(self.repo, geogit.HEAD, "parks")
    	tree.exportShp(exportPath)
    	self.assertTrue(os.path.exists(exportPath))
