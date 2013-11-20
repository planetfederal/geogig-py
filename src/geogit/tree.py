class Tree(object):
    
    '''An object representing a tree path for a given commit'''
    
    def __init__(self, repo, ref, path):
        self.repo = repo
        self.ref = ref
        self.path = path
        
    def trees(self):
        return self.repo.trees(self.ref, self.path)
        
    def features(self):
        return self.repo.features(self.ref, self.path)
    
    def children(self):        
        return self.repo.children(self.ref, self.path)
    
    def exportshp(self, shapefile):
        self.repo.exportshp(self.ref, self.path, shapefile)
    
    def __str__(self):
        return self.ref + ":" + self.path
