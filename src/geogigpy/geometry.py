class Geometry(object):

    def __init__(geom, crs):
        self.geom = geom
        self.crs = crs

    def __str__(self):
        return self.geom

