import os
import time
import shutil
from geogit.repo import Repository
from geogit.geogitexception import GeoGitException
from geogit.commitish import Commitish
from geogit.diff import TYPE_MODIFIED
import unittest
import geogit

class GeogitRepositoryTest(unittest.TestCase):
        
    repo = Repository(os.path.join(os.path.dirname(__file__), 'data/testrepo'))

    def getTempRepoPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')


    def getClonedRepo(self):
        src = self.repo.url
        dst = self.getTempRepoPath()
        shutil.copytree(src, dst)
        return Repository(dst)

    def testCreateEmptyRepo(self):    
        repoPath =  self.getTempRepoPath()         
        Repository(repoPath, init = True)    
    
    def testRevParse(self):
        headid = self.repo.revparse("HEAD")
        entries = self.repo.log()
        self.assertEquals(entries[0].commit.commitid, headid)

    def testRevParseWrongReference(self):
        try:
            self.repo.revparse("WrOnGReF")
            self.fail()
        except GeoGitException, e:
            pass

    def testLog(self):
        entries = self.repo.log()
        self.assertEquals(4, len(entries))
        commit = entries[0].commit
        self.assertEquals("message_4", commit.message)        
        diffset = entries[0].diffset
        #TODO: add more 

    def testLogInBranch(self):
        entries = self.repo.log("mybranch")
        self.assertEquals(4, len(entries))

    def testTreesAtHead(self):
        trees = self.repo.trees()
        self.assertEquals(1, len(trees))
        self.assertEquals("parks", trees[0].path)            
        self.assertEquals(geogit.HEAD, trees[0].ref)        
    
    def testTreesAtCommit(self):
        head = self.repo.head()
        parent = head.parent()
        trees = parent.trees()
        self.assertEquals(1, len(trees))
        self.assertEquals("parks", trees[0].path)
        entries = self.repo.log()      
        id = self.repo.revparse(trees[0].ref)  
        self.assertEquals(entries[1].commit.commitid, id)   

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
        diffs = self.repo.diff(geogit.HEAD, Commitish(self.repo, geogit.HEAD).parent().ref)
        self.assertEquals(1, len(diffs))
        self.assertEquals("parks/5", diffs[0].path)
        self.assertEquals(TYPE_MODIFIED, diffs[0].type())


    def testFeatureData(self):
        feature = self.repo.feature(geogit.HEAD, "parks/1")
        data = self.repo.featuredata(feature)
        self.assertEquals(8, len(data))
        self.assertEquals("Public", data["usage"])
        self.assertTrue("owner" in data)
        self.assertTrue("agency" in data)
        self.assertTrue("name" in data)
        self.assertTrue("parktype" in data)
        self.assertTrue("area" in data)
        self.assertTrue("perimeter" in data)
        self.assertTrue("the_geom" in data)

    def testFeatureDataNonExistentFeature(self):
        feature = self.repo.feature(geogit.HEAD, "wrongpath/wrongname")
        try:
            self.repo.featuredata(feature)
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
        self.assertTrue("message", log[4].commit.message)

    def testCreateReadAndDeleteBranch(self):        
        branches = self.repo.branches()
        self.assertEquals(2, len(branches))
        self.repo.createbranch(geogit.HEAD, "anewbranch")
        branches = self.repo.branches()
        self.assertEquals(3, len(branches))
        names = [c[0] for c in branches]        
        self.assertTrue("anewbranch" in names)
        self.repo.deletebranch("anewbranch")
        branches = self.repo.branches()
        self.assertEquals(2, len(branches))
        names = [c[0] for c in branches]
        self.assertFalse("anewbranch" in names)

    def testGetWrongBranch(self):
        try:
            self.repo.branch("WrOnGReF")
            self.fail()
        except GeoGitException, e:
            pass

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
        tags = self.repo.tags()
        self.assertEquals(2, len(tags))
        self.repo.createtag(self.repo.head(), "anewtag", "message1")
        tags = self.repo.tags()
        self.assertEquals(3, len(tags))
        names = [tag[0] for tag in tags]
        self.assertTrue("anewtag" in names)
        self.repo.deletetag("anewtag")
        tags = self.repo.tags()
        self.assertEquals(2, len(tags))
        names = [tag[0] for tag in tags]
        self.assertFalse("anewtag" in names)