import re
from commitish import Commitish
from tag import Tag
import geogig
from geogigexception import GeoGigException
from feature import Feature
from tree import Tree
from utils import mkdir
from py4jconnector import Py4JCLIConnector
from geogigserverconnector import GeoGigServerConnector
import tempfile
import datetime
import re

def _resolveref(ref):
    '''
    Tries to resolve the pased object into a string representing a commit reference 
    (a SHA-1, branch name, or something like HEAD~1)
    This should be called by all commands using references, so they can accept both
    strings and Commitish objects indistinctly
    '''
    if ref is None:
        return None
    if isinstance(ref, Commitish):
        return ref.ref
    elif isinstance(ref, basestring):
        return ref
    else:
        return str(ref)

SHA_MATCHER = re.compile(r"\b([a-f0-9]{40})\b")

class Repository(object):

    _logcache = None

    def __init__(self, url, connector = None, init = False, initParams = None):
        '''
        url: The url of the repository. Only file paths are supported so far. Remote repos are not supported
        
        connector: the connector to use to communicate with the repository
        
        init: True if the repository should be initialized
        '''
        self.url = url
        self.connector = Py4JCLIConnector() if connector is None else connector
        if init:
            try:
                mkdir(url)
            except Exception, e:
                raise GeoGigException("Cannot create repository folder.\nCheck that path is correct and you have permission")

        self.connector.setRepository(self)
        try:
            self.connector.checkisrepo()
            isAlreadyRepo = True
        except GeoGigException, e:
            isAlreadyRepo = False

        if init:
            if isAlreadyRepo:
                raise GeoGigException("Cannot init, the folder is already a geogig repository")
            else:
                self.init(initParams)
        self.connector.checkisrepo()

        self.cleancache()

    @staticmethod
    def newrepofromclone(url, path, connector = None, username = None, password = None):
        '''
        Clones a given repository into a local folder and returns a repository object representing it
        
        url: the url of the repo to clone
        
        path: the path to clone the repo into
        
        connector: the connector to use to communicate with the repository        
        '''
        connector = Py4JCLIConnector() if connector is None else connector
        connector.clone(url, path, username, password)
        return Repository(path, connector)

    def createdat(self):
        '''Returns the creation date of this repository'''
        return self.connector.createdat()

    def cleancache(self):
        self._logcache = None

    def description(self):
        '''Returns the description of this repository'''
        #TODO
        return ''

    def revparse(self, rev):
        '''Returns the SHA-1 of a given element, represented as a string'''
        if SHA_MATCHER.match(rev) is not None:
            return rev
        else:
            return self.connector.revparse(rev)


    @property
    def head(self):
        '''Returns a Commitish representing the current HEAD'''
        return self.connector.head()

    @property
    def index(self):
        '''Returns a Commitish representing the index'''
        return Commitish(self, geogig.STAGE_HEAD)

    @property
    def workingtree(self):
        '''Returns a Commitish representing workingtree'''
        return Commitish(self, geogig.WORK_HEAD)

    @property
    def master(self):
        '''Returns a Commitish representing the master branch'''
        return Commitish(self, geogig.MASTER)

    def isdetached(self):
        '''Returns true if the repos has a detached HEAD'''
        return  self.head.id == self.head.ref


    def synced(self, branch = geogig.HEAD, credentials = None):
        '''
        Returns a tuple with number of (ahead, behind) commits between this repo and a remote
        It uses the passed branch or, if not passed, the current branch
        If the repository is headless, or if not remote is defined, it will throw an exception 
        It uses the "origin" remote if it exists, otherwise it uses the first remote available.
        If the remote requires authentication, a tuple of (username,password) must be passed
        in the credentials parameter
        '''
        if (branch == geogig.HEAD and self.isdetached()):
            raise GeoGigException("Cannot use current branch. The repository has a detached HEAD")

        remotes = self.remotes
        if remotes:
            if "origin" in remotes:
                remote = remotes["origin"]
                remotename = "origin"
            else:
                remotename = remotes.keys()[0]
                remote = remotes.values()[0]
        else:
            raise GeoGigException("No remotes defined")

        if isremoteurl(remote):
            repo = Repository(remote, GeoGigServerConnector(credentials))
        else:
            conn = self.connector.__class__()
            repo = Repository(remote[len("file:/"):], conn)

        localtip = self.revparse(branch)
        remotetip = repo.revparse(branch)
        if remotetip == localtip:
            return 0, 0

        if remotetip == geogig.NULL_ID:
            log = self.log(branch)
            push = len(log)
            pull = 0
        else:
            trackedbranchhead = self.revparse("refs/remotes/" + remotename + "/" + branch)
            log = self.log(branch, trackedbranchhead)
            push = len(log)
            log = repo.log(branch, trackedbranchhead)
            pull = len(log)
        return push, pull


    def mergemessage(self):
        '''
        Return the merge message if the repo is in a merge operation stopped due to conflicts.
        Returns an empty string if it is not the case
        '''
        return self.connector.mergemessage()

    def log(self, tip = None, sincecommit = None, until = None, since = None, path = None, n = None):
        '''
        Returns a list of Commit starting from the passed tip ref, or HEAD if there is no passed ref,
        and up to the sincecommit, if passed, or to first commit in the history if not.
        If a path is passed, it only returns commits in which that path was modified
        Date limits can be passed using the since and until parameters
        A maximum number of commits can be set using the n parameter
        '''
        tip = tip or geogig.HEAD
        if path is not None or tip != geogig.HEAD or n is not None or since is not None or until is not None or sincecommit is not None:
            return self.connector.log(_resolveref(tip), _resolveref(sincecommit), _resolveref(until), _resolveref(since), path, n)
        if self._logcache is None:
            self._logcache = self.connector.log(_resolveref(tip), _resolveref(sincecommit), _resolveref(until), _resolveref(since), path, n)
        return self._logcache

    def commitatdate(self, t):
        '''Returns a Commit corresponding to a given instant, which is passed as a datetime.datetime'''
        epoch = datetime.datetime.utcfromtimestamp(0)
        delta = t - epoch
        milisecs = int(delta.total_seconds()) * 1000
        log = self.connector.log(geogig.HEAD, until = str(milisecs), n = 1)
        if log:
            return log[0]
        else:
            raise GeoGigException("Invalid date for this repository")


    @property
    def trees(self):
        return self._trees()

    def _trees(self, ref = geogig.HEAD, path = None, recursive = False):
        '''Returns a set of Tree objects with all the trees for the passed ref and path'''
        return [e for e in self.children(ref, path, recursive)  if isinstance(e, Tree)]

    def features(self, ref = geogig.HEAD, path = None, recursive = False):
        '''Returns a set of Feature objects with all the features for the passed ref and path'''
        return [e for e in self.children(ref, path, recursive)  if isinstance(e, Feature)]

    def children(self, ref = geogig.HEAD, path = None, recursive = False):
        '''Returns a set of Tree and Feature objects with all the children for the passed ref and path'''
        return self.connector.children(_resolveref(ref), path, recursive)

    @property
    def branches(self):
        ''' Returns a dict with branch names as keys and branch refs as values'''
        return self.connector.branches()

    @property
    def tags(self):
        '''Returns a dict with tag names as keys and tag objects as values'''
        tags = self.connector.tags()
        tags = {k:Tag(self, v, k) for k, v in tags.iteritems()}
        return tags

    def clone(self, path):
        '''Clones this repo in the specified path. Returns a reference to the cloned repo'''
        url = self.url.replace('\\', '/')
        self.connector.clone(url, path)
        return Repository(path, self.connector.__class__(), False)

    def createbranch(self, ref, name, force = False, checkout = False):
        '''Creates a new branch in the repo. Returns the commitish representing the branch'''
        if checkout:
            self.cleancache()
        return self.connector.createbranch(_resolveref(ref), name, force, checkout)



    def deletebranch(self, name):
        '''Deletes the passed branch'''
        self.connector.deletebranch(name)

    def createtag(self, ref, name, message):
        '''Creates a new tag, with the passed message'''
        self.connector.createtag(_resolveref(ref), name, message)

    def deletetag(self, name):
        '''Deletes the passed tag'''
        self.connector.deletetag(name)

    def diff(self, refa = geogig.HEAD, refb = geogig.WORK_HEAD, path = None):
        '''Returns a list of DiffEntry representing the changes between 2 commits.
        If a path is passed, it only shows changes corresponding to that path'''
        return self.connector.diff(_resolveref(refa), _resolveref(refb), path)

    def difftreestats(self, refa = geogig.HEAD, refb = geogig.WORK_HEAD):
        '''Returns a dict with tree changes statistics for the passed refs. Keys are paths, values are tuples
        in the form  (added, deleted, modified) corresponding to changes made to that path'''
        return self.connector.difftreestats(_resolveref(refa), _resolveref(refb))

    def treediff(self, path, refa = geogig.HEAD, refb = geogig.WORK_HEAD):
        '''Returns a tuple attributes, features with a description of features changed between the specified refs
        Attributes is a dict with attribute names as keys and the description of the attribute as value
        Features is a list, with each element being another list representing a feature and the changes 
        in it between the two specifed versions.
        The length of this list is the same as the one of attributes dictionary
        The value for an attribute is a tuple of (change_type, old value, new value) in case the change for the
        attribute is a modification, or (change_type, value), if the change is a removal, addition or
        unmodified'''
        return self.connector.treediff(path, _resolveref(refa), _resolveref(refb))

    def unstaged(self):
        '''Returns a list of diffEntry with the differences between staging area and working tree'''
        return self.diff(geogig.STAGE_HEAD, geogig.WORK_HEAD);

    def staged(self):
        '''Returns a list of diffEntry with the differences between HEAD and Staging area'''
        return self.diff(geogig.HEAD, geogig.STAGE_HEAD);

    def notindatabase(self):
        '''Returns a list of diffEntry with the differences between HEAD and Working Tree'''
        return self.diff(geogig.HEAD, geogig.WORK_HEAD);

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
        '''Checks out the passed ref into the working tree.
        If a path list is passed, it will just checkout those paths.
        If force is True, it will check out even if the working tree is not clean'''
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

    def solveconflict(self, path, attributes):
        '''
        Solves a conflict at the specified path with a new feature defined by the passed attributes.
        Attributes are passed in a dict with attribute names as keys and attribute values as values.
        This can be used only with features containing one and only one geometry attribute
        '''
        self.reset(geogig.HEAD, path = path)
        self.insertfeature(path, attributes)
        self.add([path])

    def solveconflicts(self, paths, version = geogig.OURS):
        '''
        Solves the specified paths with one of the corresponding existing versions (ours or theirs)
        Version is specified using geogig.OURS or geogig.THEIRS
        '''
        self.connector.solveconflicts(paths, version)


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
        Raises an UnconfiguredUserException if there is no user configured and it cannot commit
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
        Values are converted to appropriate types when possible, otherwise they are stored
        as the string representation of the attribute
        '''
        data = self.connector.featuredata(_resolveref(ref), path)
        if len(data) == 0:
            raise GeoGigException("The specified feature does not exist")
        return data

    def featuretype(self, ref, tree):
        '''Returns the featuretype of a tree as a dict in the form attrib_name : attrib_type_name'''
        return self.connector.featuretype(ref, tree)

    def versions(self, path):
        '''
        Returns all versions os a given feature.
        It returns a dict with Commit objects as keys, and feature data for the corresponding
        commit as values. Feature data is another dict with attributes 
        names as keys and tuples of (attribute_value, attribute_type_name) as values.
        Values are converted to appropriate types when possible, otherwise they are stored 
        as the string representation of the attribute
        '''
        entries = self.log(geogig.HEAD, path = path)
        refs = [entry.ref + ":" + path for entry in entries]
        versions = []
        if refs:
            features = self.connector.featuresdata(refs)
            for entry, ref in zip(entries, refs):
                versions.append((entry, features[ref]))
        return versions

    def featurediff(self, ref, ref2, path):
        '''
        Returns a dict with attributes that have changed in the specified feature path between the specified refs
        Keys are attribute names. Values are tuples of "(oldvalue, newvalue)"
        If the feature has been added, oldvalue = None
        If the feature has been removed, newvalue = None
        Values are converted to appropriate types if possible, otherwise they are stored as strings
        '''
        return self.connector.featurediff(_resolveref(ref), _resolveref(ref2), path)

    def reset(self, ref, mode = geogig.RESET_MODE_HARD, path = None):
        '''Resets the current branch to the passed reference'''
        self.connector.reset(ref, mode, path)
        self.cleancache()


    def exportshp(self, ref, path, shapefile):
        self.connector.exportshp(_resolveref(ref), path, shapefile)

    def exportsl(self, ref, path, database, user = None, table = None):
        '''Export to a SpatiaLite database'''
        self.connector.exportsl(_resolveref(ref), path, database, user, table)

    def exportpg(self, ref, path, table, database, user, password = None, schema = None, host = None, port = None, overwrite = False):
        self.connector.exportpg(_resolveref(ref), path, table, database, user, password, schema, host, port, overwrite)

    def importgeojson(self, geojsonfile, add = False, dest = None, idAttribute = None, geomName = None, force = False):
        self.connector.importgeojson(geojsonfile, add, dest, idAttribute, geomName, force)

    def importshp(self, shpfile, add = False, dest = None, idAttribute = None, force = False):
        self.connector.importshp(shpfile, add, dest, idAttribute, force)

    def importpg(self, database, user = None, password = None, table = None, schema = None,
                 host = None, port = None, add = False, dest = None, force = False, idAttribute = None):
        self.connector.importpg(database, user, password, table,
                                schema, host, port, add, dest, force, idAttribute)

    def importsl(self, database, table, add = False, dest = None):
        self.connector.importsl(database, table, add, dest)

    def exportdiffs(self, commit1, commit2, path, filepath, old = False, overwrite = False):
        '''Exports the differences in a given tree between to commits, creating a shapefile 
        with the changed features corresponding to the newest of them, or the oldest if old = False'''
        self.connector.exportdiffs(_resolveref(commit1), _resolveref(commit2), path, filepath, old, overwrite)

    def insertfeature(self, path, attributes):
        '''
        Inserts a feature to the working tree.

        The attributes are passed in a dict with attribute names as keys and attribute values as values.
        There must be one and only one geometry attribute, with a Geometry object.  
        
        It will overwrite any feature in the same path, so this can be used to add a new feature or to 
        modify an existing one
        '''
        self.connector.insertfeatures({path : attributes})

    def insertfeatures(self, features):
        '''
        Inserts a set of features into the working tree.

        Features are passed in a dict with paths as keys and attributes as values 
        The attributes for each feature are passed in a dict with attribute names as keys and attribute values as values.
        There must be one an only one geometry attribute, with a Geometry object.
        
        It will overwrite any feature in the same path, so this can be used to add new features or to 
        modify existing ones
        '''
        self.connector.insertfeatures(features)

    def removefeatures(self, paths):
        '''Removes the passed features paths from the working tree and index, so they are no longer versioned'''
        self.connector.removepaths(paths)

    def removetrees(self, paths):
        '''Removes the passed tree paths from the working tree and index, so they are no longer versioned'''
        self.connector.removepaths(paths, True)


    def commonancestor(self, refa, refb):
        '''
        Returns the common ancestor of the two passed references as a commitish object
        Returns None if no common ancestor exists for the passed references
        '''
        return self.connector.commonancestor(refa, refb)

    def merge(self, ref, nocommit = False, message = None):
        '''Merges the passed ref into the current branch'''
        self.connector.merge(_resolveref(ref), nocommit, message)
        self.cleancache()

    def rebase(self, ref):
        '''Rebases the current branch using the passed ref'''
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
        Continues a rebase operation that was stopped due to conflicts
        Raises a GeoGigException if the repo is not clean and cannot continue the operation
        Does nothing if the repo is not in a conflicted state caused by a rebase operation
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

    def addremote(self, name, url, username, password):
        '''Adds a new remote'''
        self.connector.addremote(name, url, username, password)

    def removeremote(self, name):
        '''Removes a remote'''
        self.connector.removeremote(name)

    def ismerging(self):
        '''Returns true if the repo is in the middle of a merge stopped due to conflicts'''
        return self.connector.ismerging()

    def isrebasing(self):
        '''Returns true if the repo is in the middle of a rebase stopped due to conflicts'''
        return self.connector.isrebasing()

    def downloadosm(self, osmurl, bbox, mappingorfile = None):
        '''Downloads from a OSM server using the overpass API.
        The bbox parameter defines the extent of features to download.
        Accepts a mapping object or a string with the path to a mapping file'''
        mappingfile = None
        if mappingorfile is not None:
            mappingfile = self._mapping(mappingorfile)
        self.connector.downloadosm(osmurl, bbox, mappingfile)
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
        '''
        Imports an osm file.        
        Accepts a mapping object or a string with the path to a mapping file to define an import mapping
        '''
        mappingfile = None
        if mappingorfile is not None:
            mappingfile = self._mapping(mappingorfile)
        self.connector.importosm(osmfile, add, mappingfile)

    def exportosm(self, osmfile, ref = None, bbox = None):
        '''
        Exports the OSM data in the repository to an OSM XML file
        A bounding box can be passed to be used as a filter. 
        It is passed as a tuple of 4 elements containing the boundary coordinates in the form (S, W, N, E)
        '''
        self.connector.exportosm(osmfile, _resolveref(ref), bbox)

    def exportosmchangeset(self, osmfile, changesetid = None, refa = None, refb = None):
        '''
        Exports the difference between the osm data in two commits as a osm changeset.
        An alternative changeset id can be used to replace negative ids if they exist
        '''
        self.connector.exportosmchangeset(osmfile, changesetid, _resolveref(refa), _resolveref(refb))

    def maposm(self, mappingorfile):
        '''Applies a mapping to the OSM data in the repo.
        The mapping can be passed as a file path to a mapping file, or as a OSMMapping object'''
        mappingfile = self._mapping(mappingorfile)
        self.connector.maposm(mappingfile)

    def show(self, ref):
        '''Returns the description of an element, as printed by the GeoGig show command'''
        return self.connector.show(_resolveref(ref))

    def config(self, param, value, global_ = False):
        '''Configures a geogig parameter with a the passed value'''
        return self.connector.config(param, value, global_)

    def getconfig(self, param):
        '''Returns the current value for a given parameter'''
        return self.connector.getconfig(param)

    def pull(self, remote = geogig.ORIGIN, branch = None, rebase = False):
        '''
        Pulls from the specified remote and specified branch.
        If no branch is provided, it will use the name of the current branch, unless the repo is headless. 
        In that case, and exception will be raised
        If rebase == True, it will do a rebase instead of a merge
        '''
        if branch == None and self.isdetached():
            raise GeoGigException("HEAD is detached. Cannot pull")
        branch = branch or self.head.ref
        self.connector.pull(remote, branch, rebase)
        self.cleancache()

    def push(self, remote, branch = None, all = False):
        '''
        Pushes to the specified remote and specified branch. 
        If no branch is provided, it will use the name of the current branch, unless the repo is headless.        
        In that case, and exception will be raised.
        if all == True, it will push all branches and ignore the branch. 
        '''
        if branch is None and self.isdetached():
            raise GeoGigException("HEAD is detached. Cannot push")
        branch = branch or self.head.ref
        return self.connector.push(remote, branch, all)

    def init(self, initParams = None):
        '''
        Inits the repository.
        Init params is a dict of paramName : paramValues to be supplied to the init command
        '''
        self.connector.init(initParams)

def isremoteurl(url):
    ##This code snippet has been taken from the Django source code
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)

