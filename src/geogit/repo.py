from commitish import Commitish
from cliconnector import CLIConnector
import geogit
from geogitexception import GeoGitException
from feature import Feature
from tree import Tree

class Repository:
    
    usecache = True
    _logcache = []

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

    def cleancache(self):
        self._logcache = []
        
    def revparse(self, rev):
        '''returns the SHA-1 of a given element, represented as a string'''
        return self.connector.revparse(rev)

    def head(self):
        '''Returns a Commitish representing the current HEAD'''
        return self.connector.head()
    
    def log(self, ref = None, path = None):
        '''
        Returns a list of Commitish starting from the passed ref, or HEAD if there is no passed ref.
        If a path is passed, it only returns commits in which that path was modified
        '''        
        return self.connector.log(ref or geogit.HEAD)
    
    def trees(self, ref = geogit.HEAD, path = None, recursive = False): 
        '''returns a set of Tree objects with all the trees for the passed ref and path'''       
        return [e for e in self.children(ref, path, recursive)  if isinstance(e, Tree)]
    
    def features(self, ref = geogit.HEAD, path = None, recursive = False): 
        '''returns a set of Feature objects with all the features for the passed ref and path'''                  
        return [e for e in self.children(ref, path, recursive)  if isinstance(e, Feature)]
    
    def children(self, ref = geogit.HEAD, path = None, recursive = False): 
        '''Returns a set of Tree and Feature objects with all the trees for the passed ref and path'''          
        return self.connector.children(ref, path, recursive)                   
            
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
        '''clones this repo in the specified path. Returns a reference to the cloned repo'''
        url = self.url.replace('\\', '/')
        self.connector.clone(url, path)
        return Repository(path, self.connector, False)
    
    def createbranch(self, commitish, name, force = False, checkout = False):
        '''Creates a new branch in the repo. Returns the commitish representing the branch'''
        return self.connector.createbranch(commitish, name, force, checkout)

    def deletebranch(self, name):
        '''deletes the passed branch'''
        self.connector.deletebranch(name)

    def createtag(self, ref, name, message):
        '''creates a new tag'''
        self.connector.createtag(ref, name, message)

    def deletetag(self, name):
        '''Deletes the passed tag'''
        self.connector.deletetag(name)
    
    def diff(self, refa = geogit.HEAD, refb = geogit.WORK_HEAD):
        '''Returns a list of DiffEntry representing the changes between 2 commits'''
        return self.connector.diff(refa, refb)
    
    def unstaged(self):
        '''Returns a list of diffEntry with the differences between staging area and working tree'''
        return self.diff(geogit.STAGE_HEAD, geogit.WORK_HEAD);
    
    def staged(self):
        '''Returns a list of diffEntry with the differences between HEAD and Staging area'''
        return self.diff(geogit.HEAD, geogit.STAGE_HEAD);
    
    def notindatabase(self):
        '''Returns a list of diffEntry with the differences between HEAD and Working Tree'''
        return self.diff(geogit.HEAD, geogit.WORK_HEAD);
    
    def conflicts(self):
        '''Returns a list of tuples, each of them with the 3 versions defining a conflict'''
        return self.connector.conflicts()
    
    def checkout(self, ref, paths = None):
        '''Checks out the passed ref'''
        return self.connector.checkout(ref)
    
    def updatepathtoref(self, ref, paths):
        '''Updates the element in the passed paths to the version corresponding to the passed ref'''
        return self.connector.checkout(ref, paths)    

    def add(self, paths = []):
        '''Adds the passed paths to the staging area. If no paths are passed, it will add all the unstaged ones'''
        return self.connector.add(paths)

    def addandcommit(self, message, paths = []):
        self.add(paths)
        return self.commit(message, paths)

    def commit(self, message, paths = []):
        return self.connector.commit(message, paths)
    
    def blame(self, path):
        '''
        Returns authorship information for the passed path

        It is returned as a dict, with attribute names as keys.
        Values are tuples of (value, commitid, authorname)
        '''
        return self.connector.blame(path)
    
    def feature(self, ref, path): 
        '''Returns a Feature object corresponding to the passed ref and path'''
        return Feature(self, ref, path)    

    def featuredata(self, ref, path):
        '''
        Returns the attributes of a given feature, as a dict with attributes 
        names as keys and tuples of (attribute_value, attribute_type_name) as values.
        Values are converted to appropiate types when possible, otherwise they are stored 
        as the string representation of the attribute
        '''
        data = self.connector.featuredata(ref, path)
        if len(data) == 0:            
            raise GeoGitException("The specified feature does not exist")
        return data
    
    def versions(self, path):
        '''
        Returns all versions os a given feature.
        It returns a dict with Commit objects as keys, and feature data for the corresponding
        commit as values. Feature data is another dict with attributes 
        names as keys and tuples of (attribute_value, attribute_type_name) as values.
        Values are converted to appropiate types when possible, otherwise they are stored 
        as the string representation of the attribute
        '''            
        entries = self.log(geogit.HEAD, path)        
        refs = [entry.ref + ":" + path for entry in entries]
        features = self.connector.featuresdata(refs)                
        versions = []
        for i, ref in enumerate(features):
            feature = features[ref]
            commit = entries[i]
            versions.append((commit, feature))
        return versions
    
    def featurediff(self, ref, ref2, path):
        '''
        Returns a dict with attributes that have changed in the specified path between the specified refs
        Keys are attribute names. Values are tuples of "(oldvalue, newvalue)"
        Both values are always strings
        '''
        return self.connector.featurediff(ref, ref2, path)
    
    def reset(self, ref, mode = geogit.RESET_MODE_HARD):
        return self.connector.reset(ref, mode)
       
    def exportshp(self, ref, path, shapefile):
        self.connector.exportshp(ref, path, shapefile)
        
    def exportsl(self, ref, path, database):
        '''export to a SpatiaLite database'''
        self.connector.exportsl(ref, path, database)        
    
    def importosm(self, osmfile, add):
        self.connector.importosm(osmfile, add)
        
    def importshp(self, shpfile, add = False, dest = None):
        self.connector.importshp(shpfile, add, dest)

    def addfeature(path, attributes):
        pass

    def removefeature(path):
        pass

    def modifyfeature(self, path, attributes):
        '''
        Modifies a feature, inserting a different version in the working tree.

        The attributes are passed in a map with attribute names as keys and attribute values as values.
        The attribtues must correspond to the current feature type of that feature in the working tree.
        That is, this can be used to modify attribute values, not featuretypes.        
        '''
        self.connector.modifyfeature(path, attributes)

    def downloadosm(self, osmurl, bbox):
        self.connector.downloadosm(osmurl, bbox)      
        
    def merge(self, ref, nocommit = False, message = None):
        '''Merges the passed ref into the current branch'''
        self.connector.merge(ref, nocommit, message)
        
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
        '''Returns true if the repo is in the middle of a merge stopped due to conflicts'''
        return self.connector.ismerging()
    
    def isrebasing(self):
        '''Returns true if the repo is in the middle of a rebase stopped due to conflicts'''
        return self.connector.isrebasing()            
    
    def init(self):                
        self.connector.init()