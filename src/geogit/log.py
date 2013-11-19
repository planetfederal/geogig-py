
class Logentry():
    
    def __init__(self, commit, diffset):
        self.commit = commit
        self.diffset = diffset
        
    def __str__(self):        
        return str(self.commit.commitid)
    
  