from geogit.geogitexception import GeoGitException

class Feature(object):

    def __init__(self, repo, ref, path):
        self.repo = repo
        self.ref = ref
        self.path = path
        self._attributes = None

    def attributes(self):
        if self._attributes is None:
            self.query()
        return self._attributes

    def featuretype(self):
        pass

    def diff(self, feature):
        if feature.path != self.path:
            raise GeoGitException("Cannot compare feature with different path")
        return self.repo.featurediff(self.ref, feature.ref, self.path)
    
    def exists(self):
        return len(self.attributes()) > 0

    def query(self):
        self._attributes = self.repo.featuredata(self)

    def blame(self):
        return self.repo.blame(self.path)

    def allversions(self):
        return self.repo.getversions(self.path)

    def __str__(self):
        return self.path
        
    

