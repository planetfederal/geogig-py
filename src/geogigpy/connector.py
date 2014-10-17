    
class Connector(object):
    '''Base class for connector'''
    
    def setRepository(self, repo):
        self.repo = repo 
        
    def createdat(self):
        raise NotImplementedError                            

    @staticmethod
    def clone(url, dest):        
        raise NotImplementedError  

    def geogigversion(self):
        raise NotImplementedError                    

    def revparse(self, rev):
        raise NotImplementedError
    
    def head(self):
        raise NotImplementedError          

    def isrebasing(self):
        raise NotImplementedError
    
    def ismerging(self):
        raise NotImplementedError   
        
    def mergemessage(self):
        raise NotImplementedError
        
    def checkisrepo(self):
        raise NotImplementedError
        
    
    def children(self, ref, path, recursive):
        raise NotImplementedError

    def addremote(self, name, url, username, password):
        raise NotImplementedError
        
    def removeremote(self, name):
        raise NotImplementedError     
        
    def remotes(self):
        raise NotImplementedError
        
    def log(self, tip, sincecommit, until, since, path, n):
        raise NotImplementedError
    
    def conflicts(self):
        raise NotImplementedError
            
    def solveconflicts(self, paths, version):
        raise NotImplementedError      
        
    def checkout(self, ref, paths, force):        
        raise NotImplementedError
        
    def reset(self, ref, mode, path):
        raise NotImplementedError                   

    def branches(self):    
        raise NotImplementedError
        
    def tags(self):
        raise NotImplementedError       
    
    def createbranch(self, ref, name, force, checkout):
        raise NotImplementedError

    def deletebranch(self, name):        
        raise NotImplementedError    

    def createtag(self, ref, name, message):        
        raise NotImplementedError

    def deletetag(self, name):   
        raise NotImplementedError        
       
    def add(self, paths):
        raise NotImplementedError
            
    def commit(self, message, paths):
        raise NotImplementedError
    
    def diff(self, refa, refb, path): 
        raise NotImplementedError
    
    def difftreestats(self, refa, refb):
        raise NotImplementedError
    
    def importosm(self, osmfile, add, mappingfile):
        raise NotImplementedError
        
    def exportosm(self, osmfile, ref, bbox):
        raise NotImplementedError  
    
    def exportosmchangeset(self, osmfile, changesetid, refa, refb):
        raise NotImplementedError                  
        
    def downloadosm(self, osmurl, bbox, mappingfile):
        raise NotImplementedError      
        
    def maposm(self, mappingfile):
        raise NotImplementedError
        
    def importgeojson(self, geojsonfile, add, dest, idAttribute, geomName):
        raise NotImplementedError
        
    def importshp(self, shapefile, add, dest, idAttribute):
        raise NotImplementedError
    
    def importpg(self, database, user, password, table, schema, host, port, add, dest, force, idAttribute):
        raise NotImplementedError
    
    def importsl(self, database, table, add, dest):         
        raise NotImplementedError
        
    def exportpg(self, ref, path, table, database, user, password, schema, host, port,  overwrite):
        raise NotImplementedError
        
    def exportshp(self, ref, path, shapefile):
       raise NotImplementedError
        
    def exportsl(self, ref, path, database, user, table):
        raise NotImplementedError
        
    def exportdiffs(self, commit1, commit2, path, filepath, old, overwrite):
        raise NotImplementedError
       
    def featuredata(self, ref, path):  
        raise NotImplementedError 

    def cat(self, reference):
        raise NotImplementedError

    def featuresdata(self, refs):
        raise NotImplementedError

    def featuretype(self, ref, tree):
        raise NotImplementedError
    
    def featurediff(self, ref, ref2, path):
        raise NotImplementedError
            
    def blame(self, path):
        raise NotImplementedError
    
    def commonancestor(self, refa, refb):
        raise NotImplementedError
            
    def merge (self, ref, nocommit, message):        
        raise NotImplementedError
        
    def rebase(self, commitish):
        raise NotImplementedError          
    
    def continue_(self):
        raise NotImplementedError
        
    def abort(self):
        raise NotImplementedError      
            
    def cherrypick(self, commitish):
        raise NotImplementedError
    
    def init(self, initParams):
        raise NotImplementedError
        
    def insertfeatures(self, features):
        raise NotImplementedError
                             
    def removepaths(self, paths, recursive):
        raise NotImplementedError
        
    def modifyfeature(self, path, attributes):
        raise NotImplementedError

    def applypatch(self, patchfile):
        raise NotImplementedError   
        
    def show(self, ref):
        raise NotImplementedError   
    
    def config(self,param, value, global_):
        raise NotImplementedError
        
    def getconfig(self, param):
        raise NotImplementedError
        
    def pull(self, remote, branch, rebase):
        raise NotImplementedError
        
    def push(self, remote, branch, all):
        raise NotImplementedError
