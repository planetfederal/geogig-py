from commitish import Commitish
import geogit
from geogitexception import GeoGitException
from feature import Feature
from tree import Tree
from utils import mkdir
from py4jconnector import Py4JCLIConnector

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
        self.connector = Py4JCLIConnector() if connector is None else connector
        if init:
            mkdir(url)
        self.connector.setRepository(self) 
        if init:
            self.init()        
        #Only local repos suported so far, so we check it                    
        self.connector.checkisrepo()
        self.cleancache()

    def cleancache(self):
        self._logcache = None
        
    def revparse(self, rev):
        '''returns the SHA-1 of a given element, represented as a string'''
        return self.connector.revparse(rev)

    def head(self):
        '''Returns a Commitish representing the current HEAD'''
        return self.connector.head()
    
    def isdetached(self):
        ref = self.head().ref
        resolved = self.revparse(ref)
        return ref == resolved
    
    def log(self, ref = None, path = None):
        '''
        Returns a list of Commit starting from the passed ref, or HEAD if there is no passed ref.
        If a path is passed, it only returns commits in which that path was modified
        '''     
        if self._logcache is not None and path is None or path == geogit.HEAD:  
            return self._logcache 
        else:
            self._logcache = self.connector.log(ref or geogit.HEAD, path)
            return self._logcache
    
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
        ''' Returns a list of tuples (branch_name, branch_ref) with the tips of branches in the repo'''
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
        '''Returns a list of tuples, each of them with the 3 versions defining a conflict, as Feature objects'''
        conflicts = {}
        _conflicts = self.connector.conflicts()
        for path, c in _conflicts.iteritems():
            c = tuple(Feature(self, ref, path) for ref in c)
            conflicts[path] = c
        return conflicts

    def checkout(self, ref, paths = None, force = False):
        '''Checks out the passed ref'''        
        self.connector.checkout(ref, paths, force)
        self.cleancache()
    
    def updatepathtoref(self, ref, paths):
        '''
        Updates the element in the passed paths to the version corresponding to the passed ref.
        If the path is conflicted (unmerged), it will also resolve the conflict
        '''
        for path in paths:
            self.connector.reset(ref, path = path)            
        return self.connector.checkout(ref, paths)

    def solveconflict(self, path, attributes):
        '''solves a conflict at the specified path with a new feature defined by the passed attributes.
        Attributes are passed in a dict with attribute names as keys and tuples of 
        (attribute_value, attribute_type_name) as values.'''
        self.reset(geogit.HEAD, path)
        self.modifyfeature(path, attributes)
        self.add(path)


    def add(self, paths = []):
        '''Adds the passed paths to the staging area. If no paths are passed, it will add all the unstaged ones'''
        self.connector.add(paths)

    def addandcommit(self, message, paths = []):
        self.add(paths)
        return self.commit(message, paths)

    def commit(self, message, paths = []):
        '''
        Creates a new commit with the changes in the specified paths.
        If no paths are passed, it will commit all staged features
        '''        
        self.connector.commit(message, paths)
        self.cleancache()
        #TODO: maybe add the commit instead of invaliating the whole cache
    
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
    
    def reset(self, ref, mode = geogit.RESET_MODE_HARD, path = None):
        '''Resets the current branch to the passed reference'''        
        self.connector.reset(ref, mode, path)
        self.cleancache()
        
       
    def exportshp(self, ref, path, shapefile):
        self.connector.exportshp(ref, path, shapefile)
        
    def exportsl(self, ref, path, database):
        '''Export to a SpatiaLite database'''
        self.connector.exportsl(ref, path, database)        
    
    def importosm(self, osmfile, add):
        self.connector.importosm(osmfile, add)
        
    def importshp(self, shpfile, add = False, dest = None):
        self.connector.importshp(shpfile, add, dest)

    def addfeature(self, path, attributes):
        '''
        Adds a feature to the working tree.

        The attributes are passed in a map with attribute names as keys and attribute values as values.
        The attributes must correspond to the current default feature type of the corresponding tree in the working tree.  
        Otherwise, and exception will be raised
        '''
        self.connector.addfeature(path, attributes)

    def removefeature(self, path):
        '''Removes the passed feature from the working tree and index, so it is no longer versioned'''
        self.connector.removefeature(path)

    def modifyfeature(self, path, attributes):
        '''
        Modifies a feature, inserting a different version in the working tree.

        The attributes are passed in a map with attribute names as keys and attribute values as values.
        The attributes must correspond to the current feature type of that feature in the working tree.
        That is, this can be used to modify attribute values, not featuretypes.        
        '''
        self.connector.modifyfeature(path, attributes) 
        
    def merge(self, ref, nocommit = False, message = None):
        '''Merges the passed ref into the current branch'''
        self.connector.merge(ref, nocommit, message)
        self.cleancache()        
        
    def rebase(self, ref):
        '''rebases the current branch using the passed ref'''
        self.connector.rebase(ref)
        self.cleancache()                  

    def abort(self):
        '''
        Abort a merge or rebase operation, if it was stopped due to conflicts
        Does nothing if the repo is not in a conflicted state
        '''
        self.connector.abort()

    def continue_(self):
        '''
        Abort a merge or rebase operation, if it was stopped due to conflicts
        Throws a GeoGitException if the repo is not clean and cannot continue the operation
        '''
        self.connector.continue_()
        
    def cherrypick(self, ref):
        '''Cherrypicks a commit into the current branch'''
        self.connector.cherrypick(ref)
        self.cleancache()        
        
    def remotes(self):
        '''Returns a list with tuples (remote_name, remote_url)'''
        return self.connector.remotes()
        
    def addremote(self, name, url):
        '''Adds a new remote'''
        self.connector.addremote(name, url)        
        
    def removeremote(self, name):
        '''Removes a remote'''
        self.connector.removeremote(name)    
        
    def ismerging(self):
        '''Returns true if the repo is in the middle of a merge stopped due to conflicts'''
        return self.connector.ismerging()
    
    def isrebasing(self):
        '''Returns true if the repo is in the middle of a rebase stopped due to conflicts'''
        return self.connector.isrebasing()
    
    def downloadosm(self, osmurl, bbox):
        self.connector.downloadosm(osmurl, bbox)
        self.cleancache() 
        
    def show(self, ref):
        return self.connector.show(ref)  
    
    def config(self, param, value):
        return self.connector.config(param, value)
    
    def getconfig(self, param):
        return self.connector.getconfig(param)
    
    def init(self):                
        self.connector.init()