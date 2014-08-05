from geogigexception import GeoGigException
from geometry import Geometry

class Feature(object):

    def __init__(self, repo, ref, path):
        self.repo = repo
        self.ref = ref
        self.path = path
        self._attributes = None
        self._featuretype = None

    @property
    def attributes(self):
        '''
        Returns the attributes of the feature in a dict  with attributes
        names as keys and attribute values as values.
        Values are converted to appropriate types when possible, otherwise they are stored
        as the string representation of the attribute
        '''
        if self._attributes is None:
            self.query()
        return self._attributes
    
    @property
    def attributesnogeom(self):
        '''Returns a filtered set of attributes, with only those attributes that are not geometries'''
        attrs = self.attributes
        return dict((i for i in attrs.iteritems() if not isinstance(i[1], Geometry) ))

    @property
    def geom(self):
        '''
        Returns the geometry of this feature.
        It assumes that the feature contains one and only one geometry.
        If there is no geometry, an exception is raised.
        If there are several of them, the first one found is returned.
        '''
        attrs = self.attributes 
        for v in attrs.values():
            if isinstance(v, Geometry):
                return v
        raise GeoGigException("Feature has no geometry")
    
    @property
    def geomfieldname(self):
        '''
        Returns the name of the geometry field of this feature.
        It assumes that the feature contains one and only one geometry.
        If there is no geometry, an exception is raised.
        If there are several of them, the first one found is returned.
        '''
        attrs = self.attributes 
        for k, v in attrs.iteritems():
            if isinstance(v, Geometry):
                return k
        raise GeoGigException("Feature has no geometry")
            
    def featuretype(self):  
        '''
        returns the feature type definition of the feature in a dict  with attributes 
        names as keys and attribute type names as values.
        Values are converted to appropriate types when possible, otherwise they are stored 
        as the string representation of the attribute
        '''
        if self._featuretype is None:
            self.query()
        return self._featuretype        

    def diff(self, feature):
        if feature.path != self.path:
            raise GeoGigException("Cannot compare feature with different path")
        return self.repo.featurediff(self.ref, feature.ref, self.path)
    
    def query(self):                    
        data = self.repo.featuredata(self.ref, self.path)
        if len(data) == 0:
            raise GeoGigException("Feature at the specified path does not exist")
        self._attributes = dict(( (k, v[0]) for k,v in data.iteritems()))
        self._featuretype = dict(( (k, v[1]) for k,v in data.iteritems()))

    def exists(self):
        try:
            self.attributes
            return True
        except GeoGigException, e:
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
        Values are converted to appropriate types when possible, otherwise they are stored
        as the string representation of the attribute
        '''        
        return self.repo.versions(self.path)

    def setascurrent(self):
        '''Sets this version of the feature as the current one in the working tree and index'''
        if self.exists():
            self.repo.updatepathtoref(self.ref, [self.path])
        else:
            raise GeoGigException("Feature at the specified path does not exist")

    def __str__(self):
        return self.ref + ":" + self.path
        
    

