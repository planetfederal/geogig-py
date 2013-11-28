from commitish import Commitish

class Commit(Commitish):
    
    ''' A geogit commit'''
    
    def __init__(self, repo, commitid, treeid, parent, message, authorname, authordate, commitername, commiterdate):
        self.ref = commitid
        self.repo = repo
        self.commitid = commitid
        self.treeid = treeid
        self.parent = parent
        self.message = message
        self.authorname = authorname
        self.authordate = authordate
        self.commitername = commitername
        self.commiterdate = commiterdate

    
    def __str__(self):
        s = "id " + self.commitid + "\n"
        s += "parent " + str(self.parent) + "\n"
        s += "tree " + self.treeid + "\n"
        s += "author " + self.authorname + " " + str(self.authordate) + "\n"
        s += "message " + str(self.message) + "\n" 
        
        return s
