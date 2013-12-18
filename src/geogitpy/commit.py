from commitish import Commitish
from geogit import NULL_ID

class Commit(Commitish):
    
    ''' A geogit commit'''
    
    def __init__(self, repo, commitid, treeid, parent, message, authorname, authordate, commitername, commiterdate):
        Commitish.__init__(self, repo, commitid)        
        self.repo = repo
        self.commitid = commitid
        self.treeid = treeid
        self._parent = parent or NULL_ID
        self.message = message
        self.authorname = authorname
        self.authordate = authordate
        self.commitername = commitername
        self.commiterdate = commiterdate
        
    @property
    def parent(self):
        return Commitish(self.repo, self._parent)

    def diff(self, path = None):
        '''Returns a list of DiffEntry with all changes introduced by this commitish'''
        if self._diff is None:
            self._diff = self.repo.diff(self.parent.ref, self.ref, path)
        return self._diff
    
    def difftreestats(self):
        '''Returns a dict with tree changes statistics for the passed refs. Keys are paths, values are tuples
        in the form  (added, deleted, modified) corresponding to changes made to that path'''
        return self.repo.difftreestats(self.parent.ref, self.ref)
    
    def __str__(self):
        s = "id " + self.commitid + "\n"
        s += "parent " + str(self.parent) + "\n"
        s += "tree " + self.treeid + "\n"
        s += "author " + self.authorname + " " + str(self.authordate) + "\n"
        s += "message " + str(self.message) + "\n" 
        
        return s
