import unittest
import os
from geogitpy.repo import Repository
import time

class Py4JConnectorTest(unittest.TestCase):
        
    repo = Repository(os.path.join(os.path.dirname(__file__), 'data/testrepo'))

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        dst = self.getTempPath()
        return self.repo.clone(dst)  

    def testProgress(self):        
        class Progress(object):
            ok = False
            def listener(self, i):
                self.ok = True        
        repo = Repository(os.path.join(os.path.dirname(__file__), 'data/testrepo'))
        p = Progress()
        repo.connector.setProgressListener(p.listener)
        dst = self.getTempPath()
        self.repo.clone(dst)
        self.assertTrue(p.ok)                  

    