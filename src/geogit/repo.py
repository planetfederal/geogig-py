from commitish import Commitish
from cliconnector import CLIConnector
import geogit
from geogitexception import GeoGitException
from feature import Feature

class Repository:
    
    def __init__(self, url, connector = None, init = False):
        '''
        url: The url of the repository
        connector: the connector to use to communicate with the repository
        init: True if the repository should be initialized

        '''
        self.url = url        
        self.connector = CLIConnector() if connector is None else connector
        self.connector.setRepository(self) 
        if init:
            self.init()        
        #Only local repos suported so far, so we check it                    
        self.connector.checkisrepo()
        
    def revparse(self, rev):
        return self.connector.revparse(rev)

    def head(self):
        '''Returns a Commitish representing the current HEAD'''
        return self.connector.head()
    
    def log(self, ref = None):
        '''returns a set of logentries starting from the passed ref, or HEAD if there is no passed ref'''        
        return self.connector.log(ref or geogit.HEAD)
    
    def trees(self, ref = geogit.HEAD, path = None): 
        '''returns a set of Tree objects with all the trees for the passed ref and path'''       
        return self.connector.trees(ref, path)   
    
    def features(self, ref = geogit.HEAD, path = None, recursive = False): 
        '''returns a set of Feature objects with all the features for the passed ref and path'''          
        return self.connector.features(ref, path, recursive)   
    
    def children(self, ref = geogit.HEAD, path = None): 
        '''Returns a set of Tree and Feature objects with all the trees for the passed ref and path'''          
        return self.connector.children(ref, path)                   
            
    def master(self):
        return Commitish(self, geogit.MASTER)
        
    def branches(self):        
        ''' Returns a list of Commitish with the tips of branches in the repo'''
        return self.connector.branches()
    
    def tags(self):   
        ''' Returns a list of tuple with the tags in the repo, in the form (tag_name, tag_commitid)'''     
        return self.connector.tags()
    
    def branch(self, name):        
        '''Returns a Commitish corresponding to the branch of the passed name'''
        for branch in self.branches():
            if branch[0] == name:
                return branch[1]
        raise GeoGitException("Specified branch does not exist")
    
    def clone(self, path):
        '''clones this repo in the given path. Returns a reference to the cloned repo'''
        url = self.url.replace('\\', '/')
        self.connector.clone(url, path)
        return Repository(path, self.connector, False)
    
    def createbranch(self, commitish, name, force = False, checkout = False):
        '''Creates a new branch in the repo. Returns the commitish representing the branch'''
        return self.connector.createbranch(commitish, name, force, checkout)

    def deletebranch(self, name):
        self.connector.deletebranch(name)

    def createtag(self, commitish, name, message):
        self.connector.createtag(commitish, name, message)

    def deletetag(self, name):
        self.connector.deletetag(name)
    
    def diff(self, refa = geogit.HEAD, refb = geogit.WORK_HEAD):
        '''Returns a list of DiffEntry representing the changes between 2 comits'''
        return self.connector.diff(refa, refb)
    
    def unstaged(self):
        return self.diff(geogit.STAGE_HEAD, geogit.WORK_HEAD);
    
    def staged(self):
        return self.diff(geogit.HEAD, geogit.STAGE_HEAD);
    
    def notindatabase(self):
        return self.diff(geogit.HEAD, geogit.WORK_HEAD);
    
    def conflicts(self):
        '''Returns a list of tuples, each of them with the 3 versions defining a conflict'''
        return self.connector.conflicts()
    
    def checkout(self, ref, paths = None):
        return self.connector.checkout(ref, paths)
    
    def add(self, paths = []):
        return self.connector.add(paths)

    def addandcommit(self, message, paths = []):
        self.add(paths)
        return self.commit(message, paths)

    def commit(self, message, paths = []):
        return self.connector.commit(message, paths)
    
    def blame(self, path):
        return self.connector.blame(path)
    
    def feature(self, ref, path): 
        '''Returns a Feature object corresponding to the passed ref and path'''
        return Feature(self, ref, path)

    def featuredata(self, feature):
        '''Returns the attributes of a given feature'''
        data = self.connector.featuredata(feature)
        if len(data) == 0:            
            raise GeoGitException("The specified feature does not exist")
        return 
    
    def versions(self, path):
        '''get all versions os a given feature'''
        return self.connector.versions(path)
    
    def featurediff(self, ref, ref2, path):
        return self.connector.featurediff(ref, ref2, path)
    
    def reset(self, ref, mode = geogit.RESET_MODE_HARD):
        return self.connector.reset(ref, mode)
       
    def exportshp(self, ref, shapefile):
        self.connector.exportshp(ref, shapefile)
        
    def exportsl(self, ref, database):
        self.connector.exportsl(ref, database)        
    
    def importosm(self, osmfile, add):
        self.connector.importosm(osmfile, add)
        
    def importshp(self, shpfile, add = False, dest = None):
        self.connector.importshp(shpfile, add, dest)

    def importfeature(self, path, featuredata):
        pass
        
    def downloadosm(self, osmurl, bbox):
        self.connector.downloadosm(osmurl, bbox)      
        
    def merge(self, commitish, nocommit = False, message = None):
        self.connector.merge(commitish, nocommit, message)
        
    def rebase(self, commitish):
        self.connector.rebase(commitish)  
        
    def cherrypick(self, commitish):
        self.connector.cherrypick(commitish)
        
    def show(self, ref):
        return self.connector.show(ref)
        
    def remotes(self):
        return self.connector.remotes()
        
    def addremote(self, name, url):
        self.connector.addremote(name, url)        
        
    def removeremote(self, name):
        self.connector.removeremote(name)    
        
    def ismerging(self):
        return self.connector.ismerging()
    
    def isrebasing(self):
        return self.connector.isrebasing()            
    
    def init(self):                
        self.connector.init()