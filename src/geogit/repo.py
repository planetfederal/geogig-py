from commitish import Commitish
from cliconnector import CLIConnector
import geogit
from geogitexception import GeoGitException
from feature import Feature
import os
import time
import shutil

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
    
    def log(self, ref = None, path = None):
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
        '''clones this repo in the specified path. Returns a reference to the cloned repo'''
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
        return data
    
    def versions(self, path):
        '''get all versions os a given feature'''            
        entries = self.log(geogit.HEAD, path)        
        refs = [entry.commit.ref + ":" + path for entry in entries]
        features = self.connector.featuresdata(refs)                
        versions = []
        for i, ref in enumerate(features):
            feature = features[ref]
            commit = entries[i].commit
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
        '''
        try:
            patchfile = os.path.join(self.url, str(time.time()) + ".patch")
            with open(patchfile) as f:
                ftId = Feature(geogit.WORK_HEAD, path).featuretype()
                output = self.connector.cat(ftId)
                f.write("\n".join(output[1:]))            
                f.write("\n")
                types = self.attributetypes(output[3:])
                for attr in sorted(attributes.iterkeys()):
                    try:
                        attrtype = types[attr]
                        attrvalue = attributes[attr]
                        f.write(attrtype + "\t" + str(attrvalue))
                    except KeyError, e:
                        raise GeoGitException("Attribute %s does no exist in feature to modify" % attr)

            self.connector.applypatch(patchfile)
        finally:
            shutil.rm(patchfile)

    def attributeTypes(self, lines):
        types = {}
        for line in lines:
            tokens = lines.split(" ").strip()
            types[tokens[1]] = tokens[0]
        return types
   
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