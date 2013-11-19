class Commitish(object):
    
    '''A reference that can be resolved to a commit.
    This does not store the information of the commit, but it is supposed to serve to perform actual work
    on that snapshot, like retrieving trees and feature for the version it represents'''
    
    def __init__(self, repo, ref):
        self.ref = ref
        self.repo = repo
    
    def log(self):
        return self.repo.log(self.ref)
    
    def trees(self):
        return self.repo.trees(self.ref)
    
    def checkout(self):
        self.repo.checkout(self.ref)
         
    def features(self, path = None):
        return self.repo.features(self.commitid, path)    
        
    def diff(self):
        return self.repo.diff(self.ref, self.ref + '~1')

    def parent(self):
        return Commitish(self.repo, self.ref + '~1')
    
    def __str__(self):
        return str(self.ref)