import unittest
import os
from geogit.repo import Repository
import time
import shutil
import geogit
from geogit.feature import Feature

class GeogitCommitishTest(unittest.TestCase):
        
    repo = Repository(os.path.join(os.path.dirname(__file__), 'data/testrepo'))

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        src = self.repo.url
        dst = self.getTempPath()
        shutil.copytree(src, dst)
        return Repository(dst)

    def testLog(self):
        pass

    def testTree(self):
        pass

    def testCheckout(self):
        pass


    def testDiff(self):
        pass
