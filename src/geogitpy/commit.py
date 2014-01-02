from commitish import Commitish
import datetime
from geogit import NULL_ID

class Commit(Commitish):
    
    ''' A geogit commit'''
    
    def __init__(self, repo, commitid, treeid, parent, message, authorname, authordate, committername, committerdate):
        Commitish.__init__(self, repo, commitid)        
        self.repo = repo
        self.commitid = commitid
        self.treeid = treeid
        self._parent = parent or NULL_ID
        self.message = message
        self.authorname = authorname
        self.authordate = authordate
        self.committername = committername
        self.committerdate = committerdate
        
    @staticmethod
    def fromref(repo, ref):
        id = repo.revparse(ref)
        log = repo.log(id, n = 1)
        return log[0]        
        
    @property
    def parent(self):
        if self._parent == NULL_ID: 
            return Commitish(self.repo, self._parent)
        else:
            return self.fromref(self.repo, self._parent)

    def diff(self, path = None):
        '''Returns a list of DiffEntry with all changes introduced by this commitish'''
        if self._diff is None:
            self._diff = self.repo.diff(self.parent.ref, self.ref, path)
        return self._diff
    
    def difftreestats(self):
        '''Returns a dict with tree changes statistics for the passed refs. Keys are paths, values are tuples
        in the form  (added, deleted, modified) corresponding to changes made to that path'''
        return self.repo.difftreestats(self.parent.ref, self.ref)
    
    def humantext(self):
        '''Returns a nice human-readable description of the commit'''
        headid = self.repo.revparse(self.repo.head.ref) 
        if headid == self.id:
            return "Current last commit"
        parent = self.repo.revparse(self.repo.head.ref + "~1")
        if parent == self.id:
            return "Commit before the last one"
        return "Commit from " + self.committerprettydate() +  self.committerdate.strftime(" (%m/%d/%y %H:%M)")
    
    def committerprettydate(self):
        return self.prettydate(self.committerdate)
    
    def authorprettydate(self):
        return self.prettydate(self.authordate)
        
    def prettydate(self, d):
        diff = datetime.datetime.utcnow() - d
        s = diff.seconds
        if diff.days > 30 or diff.days < 0:
            return d.strftime('%d %b %y')
        elif diff.days == 1:
            return '1 day ago'
        elif diff.days > 1:
            return '{} days ago'.format(diff.days)
        elif s < 120:
            return '1 minute ago'
        elif s < 3600:
            return '{} minutes ago'.format(s/60)
        elif s < 7200:
            return '1 hour ago'
        else:
            return '{} hours ago'.format(s/3600) 
        
    def __str__(self):
        s = "id " + self.commitid + "\n"
        s += "parent " + str(self.parent) + "\n"
        s += "tree " + self.treeid + "\n"
        s += "author " + self.authorname + " " + str(self.authordate) + "\n"
        s += "message " + str(self.message) + "\n" 
        
        return s
