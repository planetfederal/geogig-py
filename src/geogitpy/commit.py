from commitish import Commitish
from geogit import NULL_ID

class Commit(Commitish):
    
    ''' A geogit commit'''
    
    def __init__(self, repo, commitid, treeid, parent, message, authorname, authordate, commitername, commiterdate):
        Commitish.__init__(self, repo, commitid)        
        self.repo = repo
        self.commitid = commitid
        self.treeid = treeid
        self.parent = parent or NULL_ID
        self.message = message
        self.authorname = authorname
        self.authordate = authordate
        self.commitername = commitername
        self.commiterdate = commiterdate

    def diff(self):
        '''Returns a list of DiffEntry with all changes introduced by this commitish'''
        if self._diff is None:
            self._diff = self.repo.diff(self.parent, self.ref)
        return self._diff
    
    def __str__(self):
        s = "id " + self.commitid + "\n"
        s += "parent " + str(self.parent) + "\n"
        s += "tree " + self.treeid + "\n"
        s += "author " + self.authorname + " " + str(self.authordate) + "\n"
        s += "message " + str(self.message) + "\n" 
        
        return s
