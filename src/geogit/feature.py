from geogit.geogitexception import GeoGitException

class Feature(object):

    def __init__(self, repo, ref, path, featuretypeid = None):
        self.repo = repo
        self.ref = ref
        self.path = path
        self._attributes = None
        self._featuretype = featuretypeid

    def attributes(self):
        if self._attributes is None:
            self._attributes = self.repo.featuredata(self)
        return self._attributes

    def featuretype(self):
        if not self.exists():
            raise GeoGitException("Cannot get feature type. Feature does not exist")
        if self._featuretype is None:
            self._featuretype = self.repo.features(ref, path)[0].featuretype()
        return self._featuretype        

    def diff(self, feature):
        if feature.path != self.path:
            raise GeoGitException("Cannot compare feature with different path")
        return self.repo.featurediff(self.ref, feature.ref, self.path)
    
    def exists(self):
        try:
            self.attributes()
            return True
        except GeoGitException, e:
            return False

    def blame(self):
        return self.repo.blame(self.path)

    def versions(self):
        return self.repo.versions(self.path)

    def __str__(self):
        return self.path
        
    

