from tree import Tree

class Commitish(object):
    
    '''A reference that can be resolved to a commit.
    This does not store the information of the commit, but it is supposed to serve to perform actual work
    on that snapshot, like retrieving trees and feature for the version it represents'''
    
    def __init__(self, repo, ref):
        self.ref = ref
        self.repo = repo
        self._diff = None
    
    def log(self):
        '''Return the history up to this Commitish'''
        return self.repo.log(self.ref)
    
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

    def parent(self):
        '''Returns a Commitish that represents the parent of this one'''
        return Commitish(self.repo, self.ref + '~1')
    
    def __str__(self):
        return str(self.ref)