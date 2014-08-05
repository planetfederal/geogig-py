#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import time
from geogigpy.repo import Repository
import unittest
from geogigpy import geogig
from geogigpy.geogigexception import GeoGigConflictException
from testrepo import testRepo


class GeogigWorkflowTest(unittest.TestCase):

    def getTempFolderPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')
        
    def createRepo(self):
        repopath =  self.getTempFolderPath()         
        repo = Repository(repopath, init = True)
        shpfile = os.path.join(os.path.dirname(__file__), "data", "shp", "landuse", "landuse2.shp")
        repo.importshp(shpfile, False, "landuse", "fid")
        repo.addandcommit("first")        
        return repo

    def testImportExportInDifferentFormats(self):
        repopath =  self.getTempFolderPath()         
        repo = Repository(repopath, init = True)
        geojsonfile = os.path.join(os.path.dirname(__file__), "data", "geojson", "landuse.geojson")
        repo.importgeojson(geojsonfile, False, "landuse", "fid")
        repo.addandcommit("commit")
        shpfile = os.path.join(self.getTempFolderPath(), "landuse.shp")
        repo.exportshp(geogig.HEAD, "landuse", shpfile)
        repo.importshp(shpfile, False, "landuse", "fid")
        unstaged = repo.unstaged()
        self.assertEquals(0, unstaged)

    
    def testPushToExistingEmptyRepo(self):
        repopath =  self.getTempFolderPath()         
        remote = Repository(repopath, init = True)
        local = self.createRepo()
        local.addremote("myremote", repopath)
        local.push("myremote")
        self.assertEquals(remote.head.id, local.head.id)
        
    def testMoveDataBetweenClones(self):
        repo = self.createRepo()
        cloneapath = self.getTempFolderPath()  
        clonea = repo.clone(cloneapath)
        clonebpath = self.getTempFolderPath()  
        cloneb = repo.clone(clonebpath)
        log = cloneb.log()
        self.assertEquals(1, len(log))
        shpfile = os.path.join(os.path.dirname(__file__), "data", "shp", "landuse", "landuse3.shp")        
        clonea.importshp(shpfile, False, "landuse", "fid")
        clonea.addandcommit("changed attribute value")
        clonea.push("origin")
        cloneb.pull("origin","master")
        log = cloneb.log()        
        self.assertEquals(2, len(log))
        shpfile = os.path.join(os.path.dirname(__file__), "data", "shp", "landuse", "landuse4.shp")        
        cloneb.importshp(shpfile, False, "landuse", "fid")
        cloneb.addandcommit("Modifed polygon")
        cloneb.push("origin")
        clonea.pull("origin","master")
        log = clonea.log()
        self.assertEquals(3, len(log))
        
    def testWorkflowWithConflicts(self):
        repo = self.createRepo()        
        cloneapath = self.getTempFolderPath()  
        clonea = repo.clone(cloneapath)
        clonebpath = self.getTempFolderPath()        
        cloneb = repo.clone(clonebpath)
        shpfile = os.path.join(os.path.dirname(__file__), "data", "shp", "landuse", "landuse3.shp")        
        clonea.importshp(shpfile, False, "landuse", "fid")
        clonea.addandcommit("changed attribute value")
        clonea.push("origin")
        feature = cloneb.feature(geogig.HEAD, "landuse/1")
        attribs = feature.attributes
        attribs["LANDCOVER"] = "urban_areas"
        cloneb.insertfeature("landuse/1", attribs)
        cloneb.addandcommit("fixed_typo")
        feature = cloneb.feature(geogig.HEAD, "landuse/1")
        attribs = feature.attributes
        self.assertTrue("urban_areas", attribs["LANDCOVER"])              
        try:
            cloneb.pull("origin", "master")
            self.fail()
        except GeoGigConflictException:
            pass
        attribs["LANDCOVER"] = "urban"
        cloneb.solveconflict("landuse/1", attribs)
        cloneb.addandcommit(cloneb.mergemessage())
        feature = cloneb.feature(geogig.HEAD, "landuse/1")
        attribs = feature.attributes
        self.assertEquals(attribs["LANDCOVER"], "urban")
        
        
        
        
        
        
    
        