from geogit.geogitexception import GeoGitException

class Feature(object):

    def __init__(self, repo, ref, path):
        self.repo = repo
        self.ref = ref
        self.path = path
        self._attributes = None
        self._featuretype = None

    def attributes(self):
        '''
        returns the attributes of the feature in a dict  with attributes 
        names as keys and tuples of (attribute_value, attribute_type_name) as values.
        Values are converted to appropiate types when possible, otherwise they are stored 
        as the string representation of the attribute
        '''
        if self._attributes is None:
            self.query()
        return self._attributes

    def featuretype(self):        
        if self._featuretype is None:
            self.query()
        return self._featuretype        

    def diff(self, feature):
        if feature.path != self.path:
            raise GeoGitException("Cannot compare feature with different path")
        return self.repo.featurediff(self.ref, feature.ref, self.path)
    
    def query(self):                    
        data = self.repo.featuredata(self.ref, self.path)
        if len(data) == 0:
            raise GeoGitException("Feature at the specified path does not exist")
        self._attributes = {k: v[0] for k,v in data.iteritems()}
        self._featuretype = {k: v[1] for k,v in data.iteritems()}

    def exists(self):
        try:
            self.attributes()
            return True
        except GeoGitException, e:
            return False

    def blame(self):
        '''
        Returns authorship information for this feature
        It is returned as a dict, with attribute names as keys.        
        Values are tuples of (value, commitid, authorname)
        '''
        return self.repo.blame(self.path)

    def versions(self):
        '''
        Returns all versions of this feature.
        It returns a dict with Commit objects as keys, and feature data for the corresponding
        commit as values. Feature data is another dict with attributes 
        names as keys and tuples of (attribute_value, attribute_type_name) as values.
        Values are converted to appropiate types when possible, otherwise they are stored 
        as the string representation of the attribute
        '''        
        return self.repo.versions(self.path)

    def __str__(self):
        return self.path
        
    

