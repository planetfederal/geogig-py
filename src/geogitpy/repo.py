from commitish import Commitish
import geogit
from geogitexception import GeoGitException
from feature import Feature
from tree import Tree
from utils import mkdir
from py4jconnector import Py4JCLIConnector
import tempfile
import datetime

def _resolveref(ref):
    '''
    Tries to resolve the pased object into a string representing a commit reference 
    (a SHA-1, branch name, or something like HEAD~1)
    This should be called by all commands using references, so they can accept both
    strings a Commitish objects indistinctly
    ''' 
    if ref is None:
        return None
    if isinstance(ref, Commitish):
        return ref.ref
    elif isinstance(ref, basestring):
        return ref
    else:
        return str(ref)
    
class Repository(object):
        
    _logcache = None
    
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
        try:
            self.connector.checkisrepo()
            isAlreadyRepo = True
        except GeoGitException, e:
            isAlreadyRepo = False

        if init:
            if isAlreadyRepo:
                raise GeoGitException("Cannot init, the folder is already a geogit repository")
            else:
                self.init()        
        self.connector.checkisrepo()                    
        
        self.cleancache()

    def cleancache(self):
        self._logcache = None
        
    def description(self):
        '''returns the description of this repository'''
        #TODO
        return ''
    
    def revparse(self, rev):
        '''returns the SHA-1 of a given element, represented as a string'''
        return self.connector.revparse(rev)

    @property
    def head(self):
        '''Returns a Commitish representing the current HEAD'''
        return self.connector.head()
    
    @property
    def index(self):
        '''Returns a Commitish representing the index'''
        return Commitish(self, geogit.STAGE_HEAD)
    
    @property
    def workingtree(self):
        '''Returns a Commitish representing workingtree'''
        return Commitish(self, geogit.WORK_HEAD)
    
    @property
    def master(self):
        '''Returns a Commitish representing the master branch'''
        return Commitish(self, geogit.MASTER)
    
    def isdetached(self):
        '''Returns true if the repos has a detached HEAD'''
        return  self.head.id == self.head.ref
    
    def sync(self):
        '''Runs a "pull --rebase" command an then a "push" one to synchronize with the remote repository
        It uses the "origin" remote if it exists, otherwise it uses the first remote available.
        Throws an exception if the working tree an index are not clean or no remote is defined.
        It stores the time and date of the sync operation, so it can be later checked'''        
        pass
        
    def synced(self, branch = geogit.HEAD):
        '''Returns true if the repo is synced with a remote.
        It uses the passed branch or, if not passed, the current branch
        If the repository is headless, or if not remote is define,, it will throw an exception 
        It uses the "origin" remote if it exists, otherwise it uses the first remote available.'''    
        
        if (branch == geogit.HEAD and self.isdetached()):
            raise GeoGitException("Cannot use current branch. The repository has a detached HEAD")
        remotes = self.remotes
        
        if remotes:
            if "origin" in remotes:
                remote = remotes["origin"]
            else:
                remote = remotes.values()[0]
        else:
            raise GeoGitException("No remotes defined")
                
        
        conn = self.connector.__class__()
        repo = Repository(remote.strip("file:/"), conn)
        
        remoteHead = repo.revparse(branch)
        localHead = self.revparse(branch)
        
        return remoteHead == localHead
        
    
    def lastsync(self):
        '''Returns the time the last time this repository was synchronized'''
        #TODO
        return ''
            
    def log(self, tip = None, until = None, since = None, path = None, n = None):
        '''
        Returns a list of Commit starting from the passed tip ref, or HEAD if there is no passed ref.
        If a path is passed, it only returns commits in which that path was modified
        '''     
        tip = tip or geogit.HEAD
        if path is not None or until != geogit.HEAD:
            return self.connector.log(_resolveref(tip), _resolveref(until), _resolveref(since), path, n)
        if self._logcache is None:
            self._logcache = self.connector.log(_resolveref(tip), _resolveref(until), _resolveref(since), path, n)  
        return self._logcache 
    
    def commitatdate(self, t):
        '''Returns a Commit corresponding to a given instant, which is passed as a datetime.datetime'''        
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = t - epoch
        milisecs = int(delta.total_seconds()) * 1000        
        log = self.connector.log(geogit.HEAD, str(milisecs), n=1)
        if log:
            self._logcache = log
            return log[0]
        else:
            raise GeoGitException("Invalid date for this repository")
        
        
    @property
    def trees(self):
        return self._trees()
        
    def _trees(self, ref = geogit.HEAD, path = None, recursive = False): 
        '''returns a set of Tree objects with all the trees for the passed ref and path'''       
        return [e for e in self.children(ref, path, recursive)  if isinstance(e, Tree)]
    
    def features(self, ref = geogit.HEAD, path = None, recursive = False): 
        '''returns a set of Feature objects with all the features for the passed ref and path'''                  
        return [e for e in self.children(ref, path, recursive)  if isinstance(e, Feature)]
    
    def children(self, ref = geogit.HEAD, path = None, recursive = False): 
        '''Returns a set of Tree and Feature objects with all the children for the passed ref and path'''          
        return self.connector.children(_resolveref(ref), path, recursive)                           
        
    @property
    def branches(self):        
        ''' a dict with branch names as keys and branch refs as values'''
        return self.connector.branches()
    
    @property
    def tags(self):   
        ''' a dict with tag names as keys and tag commit ids as values'''     
        return self.connector.tags()
       
    def clone(self, path):
        '''clones this repo in the specified path. Returns a reference to the cloned repo'''
        url = self.url.replace('\\', '/')
        self.connector.clone(url, path)
        return Repository(path, self.connector, False)
    
    def createbranch(self, ref, name, force = False, checkout = False):
        '''Creates a new branch in the repo. Returns the commitish representing the branch'''
        return self.connector.createbranch(_resolveref(ref), name, force, checkout)

    def deletebranch(self, name):
        '''deletes the passed branch'''
        self.connector.deletebranch(name)

    def createtag(self, ref, name, message):
        '''creates a new tag'''
        self.connector.createtag(_resolveref(ref), name, message)

    def deletetag(self, name):
        '''Deletes the passed tag'''
        self.connector.deletetag(name)
    
    def diff(self, refa = geogit.HEAD, refb = geogit.WORK_HEAD, path = None):
        '''Returns a list of DiffEntry representing the changes between 2 commits.
        If a path is passed, it only shows changes corresponing to that path'''
        return self.connector.diff(_resolveref(refa), _resolveref(refb), path)
    
    def difftreestats(self, refa = geogit.HEAD, refb = geogit.WORK_HEAD):
        '''Returns a dict with tree changes statistics for the passed refs. Keys are paths, values are tuples
        in the form  (added, deleted, modified) corresponding to changes made to that path'''
        return self.connector.difftreestats(_resolveref(refa), _resolveref(refb))
        
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
        '''Returns a dict of tuples. Keys are paths, values are tuples with the 3 versions 
        defining a conflict, as Feature objects'''
        conflicts = {}
        _conflicts = self.connector.conflicts()
        for path, c in _conflicts.iteritems():
            c = tuple(Feature(self, ref, path) for ref in c)
            conflicts[path] = c
        return conflicts

    def checkout(self, ref, paths = None, force = False):
        '''Checks out the passed ref'''        
        self.connector.checkout(_resolveref(ref), paths, force)
        self.cleancache()
    
    def updatepathtoref(self, ref, paths):
        '''
        Updates the element in the passed paths to the version corresponding to the passed ref.
        If the path is conflicted (unmerged), it will also resolve the conflict
        '''
        ref = _resolveref(ref)
        for path in paths:
            self.connector.reset(ref, path = path)            
        return self.connector.checkout(ref, paths)

    def solveconflict(self, path, geom, attributes):
        '''solves a conflict at the specified path with a new feature defined by the passed attributes.
        Attributes are passed in a dict with attribute names as keys and attribute values as values.
        Geometry is a shapely geometry'''
        self.reset(geogit.HEAD, path)
        self.insertfeature(path, geom, attributes)
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
        #TODO: maybe add the commit instead of invalidating the whole cache
    
    def blame(self, path):
        '''
        Returns authorship information for the passed path

        It is returned as a dict, with attribute names as keys.
        Values are tuples of (value, commitid, authorname)
        '''
        return self.connector.blame(path)
    
    def count(self, ref, path):
        '''Returns the count of objects in a given path'''
        output = self.show(_resolveref(ref) + ":" + path)        
        return int(output.split("\n")[1][5:].strip())
    
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
        data = self.connector.featuredata(_resolveref(ref), path)
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
        entries = self.log(geogit.HEAD, path = path)     
        refs = [entry.ref + ":" + path for entry in entries]
        versions = []
        if refs:
            features = self.connector.featuresdata(refs)                        
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
        return self.connector.featurediff(_resolveref(ref), _resolveref(ref2), path)
    
    def reset(self, ref, mode = geogit.RESET_MODE_HARD, path = None):
        '''Resets the current branch to the passed reference'''        
        self.connector.reset(ref, mode, path)
        self.cleancache()
        
       
    def exportshp(self, ref, path, shapefile):
        self.connector.exportshp(_resolveref(ref), path, shapefile)
        
    def exportsl(self, ref, path, database, user = None):
        '''Export to a SpatiaLite database'''
        self.connector.exportsl(_resolveref(ref), path, database, user)        
        
    def exportpg(self, ref, path, table, database, user, password = None, schema = None, host = None, port = None):
        self.connector.exportpg(_resolveref(ref), path, table, database, user, password, schema, host, port)

    def importgeojson(self, geojsonfile, add = False, dest = None, idAttribute = None):
        self.connector.importgeojson(geojsonfile, add, dest, idAttribute)
                    
    def importshp(self, shpfile, add = False, dest = None, idAttribute = None):
        self.connector.importshp(shpfile, add, dest, idAttribute)
        
    def importpg(self, database, user = None, password = None, table = None, 
                 schema = None, host = None, port = None, add = False, dest = None):
        self.connector.importpg(database, user, password, table, schema, host, port, add, dest)           

    def exportdiffs(self, commit1, commit2, path, filepath, old = False, overwrite = False):
        '''Exports the differences in a given tree between to commits, creating a shapefile 
        each to the newest of them, or the oldest one if old = False'''
        self.connector.exportdiffs(_resolveref(commit1), _resolveref(commit2), path, filepath, old, overwrite)

    def insertfeature(self, path, geom, attributes):
        '''
        Inserts a feature to the working tree.

        The attributes are passed in a dict with attribute names as keys and attribute values as values.
        The geometry must be a Shapely object. This method only support features with a single geometry 
        
        It will overwrite any feature in the same path, so this can be used to add a new feature or to 
        modify an existing one
        '''
        self.connector.insertfeature(path, geom, attributes)

    def removefeature(self, path):
        '''Removes the passed feature from the working tree and index, so it is no longer versioned'''
        self.connector.removefeature(path)
        
    def merge(self, ref, nocommit = False, message = None):
        '''Merges the passed ref into the current branch'''
        self.connector.merge(_resolveref(ref), nocommit, message)
        self.cleancache()        
        
    def rebase(self, ref):
        '''rebases the current branch using the passed ref'''
        self.connector.rebase(_resolveref(ref))
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
        self.connector.cherrypick(_resolveref(ref))
        self.cleancache()        
    
    @property
    def remotes(self):
        '''Returns a dict with remote names as keys and remote urls as values'''
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
        '''Downloads from a OSM server using the overpass API.
        The bbox parameter defines the extent of features to download.
        Accepts a mapping or '''
        self.connector.downloadosm(osmurl, bbox, mappingOrFile = None)
        self.cleancache() 
        
        
    def _mapping(self, mappingorfile):
        if isinstance(mappingorfile, basestring):
            return mappingorfile
        else:
            try:
                f = tempfile.NamedTemporaryFile(delete = False)
                f.write(mappingorfile.asjson())   
                f.close()
                return f.name
            finally:
                f.close()
                
    def importosm(self, osmfile, add = False, mappingorfile = None):
        mappingfile = None
        if mappingorfile is not None:
            mappingfile = self._mapping(mappingorfile)        
        self.connector.importosm(osmfile, add, mappingfile)
        
    def maposm(self, mappingorfile):
        '''Applies a mapping to the OSM data in the repo.
        The mapping can be passed as a file path to a mapping file, or as a OSMMapping object'''
        mappingfile = self._mapping(mappingorfile)
        self.connector.maposm(mappingfile)

    def show(self, ref):
        '''Returns the description of an element, as printed by the GeoGit show comand'''
        return self.connector.show(_resolveref(ref))          
    
    def config(self, param, value, global_ = False):
        '''Configures a geogit parameter with a the passed value'''
        return self.connector.config(param, value, global_)
    
    def getconfig(self, param):
        '''Returns the current value for a given parameter'''
        return self.connector.getconfig(param)
    
    def pull(self, remote, branch, rebase = False):
        '''
        Pulls from the specifed remote and specified branch. 
        If no branch is provided, it will use the name of the current branch, unless the repo is headless. 
        In that case, and exception will be raised
        If rebase == True, it will do a rebase instead of a merge
        '''
        if self.isdetached():
            raise GeoGitException("HEAD is detached. Cannot pull")
        branch = branch or self.head
        return self.connector.pull(remote, branch, rebase)
    
    def push(self, remote, branch):
        '''
        Pushes to the specifed remote and specified branch. 
        If no branch is provided, it will use the name of the current branch, unless the repo is headless. 
        In that case, and exception will be raised
        '''
        if self.isdetached():
            raise GeoGitException("HEAD is detached. Cannot pull")
        branch = branch or self.head
        return self.connector.push(remote, branch)    
    
    def init(self):                
        self.connector.init()