import unittest
import os
import time
from geogigpy.commit import Commit
from testrepo import testRepo

class GeogigCommitTest(unittest.TestCase):
        
    repo = testRepo()

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        dst = self.getTempPath()
        return self.repo.clone(dst) 
    
    def testFromRef(self):
        ref = self.repo.head.ref
        commit = Commit.fromref(self.repo, ref)
        log = self.repo.log()
        headcommit = log[0]
        self.assertEqual(headcommit.ref, commit.ref)
        self.assertEqual(headcommit.committerdate, commit.committerdate)        
        
    def testCommitDiff(self):
        log = self.repo.log()
        commit = log[0]        
        diff = commit.diff()
        self.assertEquals(1, len(diff))
        self.assertEquals("parks/5", diff[0].path)        