#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
from geogigpy.repo import Repository
import unittest

class GeogigLoadTest(unittest.TestCase):            

    def getTempRepoPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')
    
    def testLargeDiff(self):
        repo = Repository(self.getTempRepoPath(), init=True)
        path = os.path.join(os.path.dirname(__file__), "data", "shp", "1", "parks.shp")
        repo.importshp(path)   
        repo.addandcommit("message")
        path = os.path.join(os.path.dirname(__file__), "data", "shp", "elevation", "elevation.shp")
        repo.importshp(path)  
        repo.addandcommit("message_2")
        s = repo.diff("HEAD~1", "HEAD")
        
    def testLargeHistory(self):
        NUMPOINTS = 6000
        repo = Repository(self.getTempRepoPath(), init=True)
        path = os.path.join(os.path.dirname(__file__), "data", "shp", "elevation", "elevation.shp")
        repo.importshp(path)
        repo.add()   
        for i in xrange(NUMPOINTS):
            feature = "elevation/" + str(i+1);            
            message = "message " + str(i+1)
            repo.commit(message, [feature])
        log = repo.log()
        
        
        