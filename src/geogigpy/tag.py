from commit import Commit

class Tag(object):
    '''An object representing a tag'''

    ROOT = None

    def __init__(self, repo, tagid, name):
        self.repo = repo
        self.tagid = tagid
        self.name = name
        self._commit = None

    @property
    def commit(self):
    	if self._commit is None:
        	lines = self.repo.connector.cat(self.tagid).split("\n")
        	commitid = lines[3][-40:]
        	self._commit = Commit.fromref(self.repo, commitid)
        return self._commit

    def __str__(self):
        return self.name + ":" + self.tagid
