from tree import Tree
import datetime

class Commitish(object):
    
    '''A reference that can be resolved to a commit.
    This does not store the information of the commit, but it is supposed to serve to perform actual work
    on that snapshot, like retrieving trees and feature for the version it represents'''
    
    def __init__(self, repo, ref):
        self.ref = ref
        self.repo = repo
        self._diff = None
        self._id = None
    
    @property
    def id(self):
        '''Returns the SHA1 ID of this commitish'''
        if self._id is None:
            self._id = self.repo.revparse(self.ref)
        return self._id
        
    def log(self):
        '''Return the history up to this commitish'''
        return self.repo.log(self.ref)
    
    @property
    def root(self):
        '''Returns a Tree that represents the root tree at this snapshot'''
        return Tree(self.repo, self.ref)
    
    def checkout(self):
        '''Checks out this commitish, and set it as the current HEAD'''
        self.repo.checkout(self.ref)
        
    def diff(self):
        '''Returns a list of DiffEntry with all changes introduced by this commitish'''
        if self._diff is None:
            self._diff = self.repo.diff(self.ref + '~1', self.ref)
        return self._diff

    @property
    def parent(self):
        '''Returns a commitish that represents the parent of this one'''
        return Commitish(self.repo, self.ref + '~1')
    
    def humantext(self):
        '''Returns a nice human-readable description of the commitish'''
        headid = self.repo.revparse(self.repo.head.ref) 
        if headid == self.id:
            return "Current branch"        
        return self.ref
        
    
    def __str__(self):
        return str(self.ref)