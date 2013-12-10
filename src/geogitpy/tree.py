class Tree(object):
    
    '''An object representing a tree path for a given commit'''
    ROOT = None

    def __init__(self, repo, ref, path = ROOT):        
        self.repo = repo
        self.ref = ref
        self.path = path
        
    @property        
    def trees(self):
        return self.repo._trees(self.ref, self.path)
        
    @property        
    def features(self):
        return self.repo.features(self.ref, self.path)
    
    @property
    def children(self):        
        return self.repo.children(self.ref, self.path)
    
    def exportshp(self, shapefile):
        '''exports this tree to the specified shapefile'''
        self.repo.exportshp(self.ref, self.path, shapefile)
    
    def __str__(self):
        return self.ref + ":" + self.path
