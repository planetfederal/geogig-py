from feature import Feature
from geogit import NULL_ID

TYPE_MODIFIED = "Modified"
TYPE_ADDED = "Added"
TYPE_REMOVED = "Removed"

class Diffentry(object):
    
    '''A difference between to references for a given path''' 
    
    def __init__(self, repo, oldcommitref, newcommitref, oldref, newref, path):
        self.repo = repo
        self.path = path
        self.oldref = oldref
        self.newref = newref
        self.oldcommitref = oldcommitref
        self.newcommitref = newcommitref

    def oldobject(self):        
        if self.oldref == NULL_ID:
            return None
        else:
            return Feature(self.repo, self.oldcommitref, self.path)
    
    def newobject(self):
        if self.newref == NULL_ID:
            return None
        else:
            return Feature(self.repo, self.newcommitref, self.path)
    
    def featurediff(self):
        return self.repo.featurediff(self.oldcommitref, self.newcommitref, self.path)
        
    
    def type(self):
        if self.oldref == NULL_ID:
            return TYPE_ADDED
        elif self.newref == NULL_ID: 
            return TYPE_REMOVED
        else:
            return TYPE_MODIFIED
    
    def __str__(self):  
        if self.oldref == NULL_ID:
            return "%s %s (%s)" % (TYPE_ADDED, self.path, self.newref) 
        elif self.newref == NULL_ID:
            return TYPE_REMOVED + " " + self.path
        else:
            return "%s %s (%s --> %s)" % (TYPE_MODIFIED, self.path, self.oldref, self.newref)
                
        
        

    
    