import os
import time
from geogitpy.repo import Repository
from geogitpy.geogitexception import GeoGitException, GeoGitConflictException
from geogitpy.commitish import Commitish
from geogitpy.diff import TYPE_MODIFIED
from geogitpy.feature import Feature
import unittest
from geogitpy import geogit
from shapely.geometry import MultiPolygon
from geogitpy.osmmapping import OSMMapping, OSMMappingRule

class GeogitRepositoryTest(unittest.TestCase):
        
    repo = Repository(os.path.join(os.path.dirname(__file__), 'data/testrepo'))

    def getTempRepoPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):        
        dst = self.getTempRepoPath()        
        return self.repo.clone(dst)        

    def testCreateEmptyRepo(self):    
        repoPath =  self.getTempRepoPath()         
        Repository(repoPath, init = True)    
    
    def testRevParse(self):
        headid = self.repo.revparse(geogit.HEAD)
        entries = self.repo.log()
        self.assertEquals(entries[0].commitid, headid)
        
    def testHead(self):
        head = self.repo.head
        self.assertEquals("master", head.ref)        
        
    def testIsDetached(self):
        repo = self.getClonedRepo()
        self.assertFalse(repo.isdetached())
        log = repo.log()
        repo.checkout(log[1].ref)
        self.assertTrue(repo.isdetached())

    def testRevParseWrongReference(self):
        try:
            self.repo.revparse("WrOnGReF")
            self.fail()
        except GeoGitException, e:
            pass

    def testLog(self):
        commits = self.repo.log()
        self.assertEquals(4, len(commits))        
        self.assertEquals("message_4", commits[0].message)        
        self.assertEquals("volaya", commits[0].authorname)                
        #TODO: add more 

    def testLogInBranch(self):
        entries = self.repo.log("conflicted")
        self.assertEquals(4, len(entries))

    def testLogEmptyRepo(self):
        repoPath =  self.getTempRepoPath()         
        repo = Repository(repoPath, init = True) 
        log = repo.log()
        self.assertFalse(log)

    def testTreesAtHead(self):
        trees = self.repo.trees()
        self.assertEquals(1, len(trees))
        self.assertEquals("parks", trees[0].path)            
        self.assertEquals(geogit.HEAD, trees[0].ref)        
    
    def testTreesAtCommit(self):
        head = self.repo.head
        parent = head.parent()
        trees = parent.root().trees()
        self.assertEquals(1, len(trees))
        self.assertEquals("parks", trees[0].path)
        entries = self.repo.log()      
        id = self.repo.revparse(trees[0].ref)  
        self.assertEquals(entries[1].commitid, id)   

    def testFeaturesAtHead(self):
        features = self.repo.features(path = "parks")
        self.assertEquals(5, len(features))
        feature = features[0]
        self.assertEquals("parks/5", feature.path)        
        self.assertEquals("HEAD", feature.ref)        

    def testChildren(self):
        children = self.repo.children() 
        self.assertEquals(1, len(children))   
        #TODO improve this test

    def testDiff(self):        
        repo = self.getClonedRepo()
        diffs = repo.diff("master", Commitish(self.repo, "master").parent().ref)
        self.assertEquals(1, len(diffs))
        self.assertEquals("parks/5", diffs[0].path)
        self.assertEquals(TYPE_MODIFIED, diffs[0].type())


    def testFeatureData(self):        
        data = self.repo.featuredata(geogit.HEAD, "parks/1")
        self.assertEquals(8, len(data))
        self.assertEquals("Public", data["usage"][0])
        self.assertTrue("owner" in data)
        self.assertTrue("agency" in data)
        self.assertTrue("name" in data)
        self.assertTrue("parktype" in data)
        self.assertTrue("area" in data)
        self.assertTrue("perimeter" in data)
        self.assertTrue("the_geom" in data)        
        self.assertTrue(isinstance(data["the_geom"][0], MultiPolygon))

    def testFeatureDataNonExistentFeature(self):        
        try:
            self.repo.featuredata(geogit.HEAD, "wrongpath/wrongname")
            self.fail()
        except GeoGitException, e:
            pass

    def testAddAndCommit(self):        
        repo = self.getClonedRepo()
        log = repo.log()
        self.assertEqual(4, len(log))
        path = os.path.join(os.path.dirname(__file__), "data", "shp", "1", "parks.shp")
        repo.importshp(path)
        repo.add()
        unstaged = repo.unstaged()
        self.assertFalse(unstaged)
        staged = repo.staged()
        self.assertTrue(staged)
        repo.commit("message")
        staged = repo.staged()
        self.assertFalse(staged)
        log = repo.log()
        self.assertEqual(5, len(log))
        self.assertTrue("message", log[4].message)
        
    def testCommitWithMessageWithBlankSpaces(self):
        repo = self.getClonedRepo()
        log = repo.log()
        self.assertEqual(4, len(log))
        path = os.path.join(os.path.dirname(__file__), "data", "shp", "1", "parks.shp")
        repo.importshp(path)
        repo.add()
        unstaged = repo.unstaged()
        self.assertFalse(unstaged)
        staged = repo.staged()
        self.assertTrue(staged)
        repo.commit("A message with blank spaces")
        staged = repo.staged()
        self.assertFalse(staged)
        log = repo.log()
        self.assertEqual(5, len(log))
        self.assertTrue("A message with blank spaces", log[4].message)

    def testCreateReadAndDeleteBranch(self): 
        repo = self.getClonedRepo()       
        branches = repo.branches
        self.assertEquals(3, len(branches))
        repo.createbranch(geogit.HEAD, "anewbranch")
        branches = repo.branches
        self.assertEquals(4, len(branches))                                
        self.assertTrue("anewbranch" in branches)
        repo.deletebranch("anewbranch")
        branches = repo.branches
        self.assertEquals(3, len(branches))        
        self.assertFalse("anewbranch" in branches)


    def testBlame(self):
        feature = self.repo.feature(geogit.HEAD, "parks/5")
        blame = self.repo.blame("parks/5")        
        self.assertEquals(8, len(blame))
        attrs = feature.attributes()
        for k,v in blame.iteritems():
            self.assertTrue(v[0], attrs[k])


    def testVersions(self):
        versions = self.repo.versions("parks/5")
        self.assertEquals(2, len(versions))

    def testFeatureDiff(self):
        diff = self.repo.featurediff(geogit.HEAD, geogit.HEAD + "~1", "parks/5")
        self.assertEquals(2, len(diff))
        self.assertTrue("area" in diff)


    def testCreateReadAndDeleteTag(self):
        repo = self.getClonedRepo()
        tags = repo.tags
        self.assertEquals(0, len(tags))
        self.repo.createtag(self.repo.head.ref, "anewtag", "message1")
        tags = self.repo.tags
        self.assertEquals(1, len(tags))        
        self.assertTrue("anewtag" in tags)
        self.repo.deletetag("anewtag")
        tags = self.repo.tags
        self.assertEquals(0, len(tags))        

    def testModifyFeature(self):
        repo = self.getClonedRepo()
        attrs = Feature(repo, geogit.HEAD, "parks/1").attributes()
        attrs["area"] = 1234.5
        repo.modifyfeature("parks/1", attrs)
        attrs = Feature(repo, geogit.WORK_HEAD, "parks/1").attributes()
        self.assertEquals(1234.5, attrs["area"])

    def testAddFeature(self):
        repo = self.getClonedRepo()
        attrs = Feature(repo, geogit.HEAD, "parks/1").attributes()        
        repo.addfeature("parks/newfeature", attrs)
        newattrs = Feature(repo, geogit.WORK_HEAD, "parks/newfeature").attributes()
        self.assertEquals(attrs, newattrs)       

    def testRemoveFeature(self):
        repo = self.getClonedRepo()        
        repo.removefeature("parks/1")
        f = Feature(repo, geogit.WORK_HEAD, "parks/1")
        self.assertFalse(f.exists())
        f = Feature(repo, geogit.STAGE_HEAD, "parks/1")
        self.assertFalse(f.exists()) 

    def testAddFeatureWithWrongFeatureType(self):
        try:
            self.repo.addfeature("parks/1", {"field1" : 1, "field2": "a"})
            self.fail()
        except GeoGitException, e:
            pass

    def testConflicts(self):
        repo = self.getClonedRepo()
        try:
            repo.merge("conflicted")
            self.fail()
        except GeoGitConflictException, e:
            pass
        conflicts = repo.conflicts()
        self.assertEquals(1, len(conflicts))
        log = repo.log()
        conflicted = repo.revparse("conflicted")                
        self.assertEquals(log[1].ref, conflicts["parks/5"][0].ref) 
        self.assertEquals(log[0].ref, conflicts["parks/5"][1].ref)
        self.assertEquals(conflicted, conflicts["parks/5"][2].ref)   
        
    def testSolveConflict(self):
        pass   

    def testIsMerging(self):
        repo = self.getClonedRepo()
        try:
            repo.merge("conflicted")
            self.fail()
        except GeoGitConflictException, e:
            pass
        self.assertTrue(repo.ismerging())
        repo.abort()        
        self.assertFalse(repo.ismerging())


    def testIsRebasing(self):
        repo = self.getClonedRepo()
        try:
            repo.rebase("conflicted")
            self.fail()
        except GeoGitConflictException, e:
            pass
        self.assertTrue(repo.isrebasing())
        repo.abort()
        self.assertFalse(repo.isrebasing())    

    def testMergeAndResolveConflict(self):
        repo = self.getClonedRepo()
        try:
            repo.merge("conflicted")
            self.fail()
        except GeoGitConflictException, e:
            self.assertTrue("conflict" in str(e))
        conflicts = repo.conflicts()
        self.assertEquals(1, len(conflicts))
        conflicts.itervalues().next()[0].setascurrent()        
        conflicts = repo.conflicts()
        self.assertEquals(0, len(conflicts))  

    def testContinueRebasing(self):
        repo = self.getClonedRepo()
        try:
            repo.rebase("conflicted")
            self.fail()
        except GeoGitConflictException, e:
            self.assertTrue("conflict" in str(e))
        conflicts = repo.conflicts()
        self.assertEquals(1, len(conflicts))
        conflicts.itervalues().next()[0].setascurrent()        
        repo.continue_()     

    def testCantContinueRebasing(self):
        repo = self.getClonedRepo()
        try:
            repo.merge("conflicted")
            self.fail()
        except GeoGitConflictException, e:
            self.assertTrue("conflict" in str(e))
        conflicts = repo.conflicts()
        self.assertEquals(1, len(conflicts))
        try:
            repo.continue_()
            self.fail()
        except GeoGitException, e:
            pass            

    def testRebase(self):
        repo = self.getClonedRepo()
        log = repo.log()        
        repo.rebase("unconflicted")
        newlog = repo.log()
        self.assertEquals(log[0].ref, newlog[0].ref)
        self.assertEquals(len(log) + 1, len(newlog))

    def testMerge(self):
        repo = self.getClonedRepo()
        commitid = repo.revparse("unconflicted")
        repo.merge("unconflicted")
        log = repo.log()
        self.assertEquals(commitid, log[1].ref)

    def testMergeNoCommit(self):
        repo = self.getClonedRepo()
        log = repo.log()
        ref = log[0].ref
        repo.merge("unconflicted", nocommit = True)
        self.assertTrue(repo.staged())
        log = repo.log()
        self.assertEquals(ref, log[0].ref)

    def testRemotes(self):
        repo = self.getClonedRepo()
        remotes = repo.remotes()
        self.assertEquals(1, len(remotes))
        repo.addremote("myremote", "http://myremoteurl.com")
        remotes = repo.remotes()
        self.assertTrue(("myremote", "http://myremoteurl.com") in remotes)
        repo.removeremote("myremote")
        remotes = repo.remotes()
        self.assertEquals(1, len(remotes))
        self.assertFalse(("myremote", "http://myremoteurl.com") in remotes)

    def testCherryPick(self):
        repo = self.getClonedRepo()
        commitid = repo.revparse("unconflicted")
        repo.cherrypick("unconflicted")
        log = repo.log()
        self.assertTrue(commitid, log[0].ref)

    def testCherryPickWithConflicts(self):
        repo = self.getClonedRepo()
        log = repo.log()
        ref = log[0].ref        
        try:
            repo.cherrypick("unconflicted")
        except GeoGitException, e:
            self.assertTrue("conflict" in str(e))
        log = repo.log()
        self.assertTrue(ref, log[0].ref)
        
    def testOsmImport(self):
        repoPath =  self.getTempRepoPath()         
        repo = Repository(repoPath, init = True)
        osmfile = os.path.join(os.path.dirname(__file__), "data", "osm", "ways.xml")        
        repo.importosm(osmfile)
        feature = Feature(repo, geogit.WORK_HEAD, "way/31045880")
        self.assertTrue(feature.exists())
        
    def testOsmImportWithMappingFile(self):
        repoPath =  self.getTempRepoPath()         
        repo = Repository(repoPath, init = True)
        osmfile = os.path.join(os.path.dirname(__file__), "data", "osm", "ways.xml")
        mappingfile = os.path.join(os.path.dirname(__file__), "data", "osm", "mapping.json")
        repo.importosm(osmfile, False, mappingfile)     
        feature = Feature(repo, geogit.WORK_HEAD, "onewaystreets/31045880")
        self.assertTrue(feature.exists())
        
    def testOsmImportWithMapping(self):
        mapping = OSMMapping()
        rule = OSMMappingRule("onewaystreets")
        rule.addfilter("oneway", "yes")
        rule.addfield("lit", "lit", geogit.TYPE_STRING)
        rule.addfield("geom", "the_geom", geogit.TYPE_LINESTRING)
        mapping.addrule(rule)
        repoPath =  self.getTempRepoPath()         
        repo = Repository(repoPath, init = True)
        osmfile = os.path.join(os.path.dirname(__file__), "data", "osm", "ways.xml")        
        repo.importosm(osmfile, False, mapping)     
        feature = Feature(repo, geogit.WORK_HEAD, "onewaystreets/31045880")
        self.assertTrue(feature.exists())
        
        
    def testOsmMapping(self):
        repoPath =  self.getTempRepoPath()         
        repo = Repository(repoPath, init = True)
        osmfile = os.path.join(os.path.dirname(__file__), "data", "osm", "ways.xml")
        mappingfile = os.path.join(os.path.dirname(__file__), "data", "osm", "mapping.json")
        repo.importosm(osmfile)
        repo.add()
        repo.commit("message")   
        repo.maposm(mappingfile)
        feature = Feature(repo, geogit.WORK_HEAD, "onewaystreets/31045880")
        self.assertTrue(feature.exists())
        




