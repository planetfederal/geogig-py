# -*- coding: utf-8 -*-

"""
***************************************************************************
    tree.py
    ---------------------
    Date                 : November 2013
    Copyright            : (C) 2013-2016 Boundless, http://boundlessgeo.com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'November 2013'
__copyright__ = '(C) 2013-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


class Tree(object):
    '''An object representing a tree path for a given commit'''

    ROOT = None

    def __init__(self, repo, ref, path=ROOT, size=None):
        self.repo = repo
        self.ref = ref
        self.path = path
        self.size = size

    @property
    def trees(self):
        return self.repo._trees(self.ref, self.path)

    @property
    def features(self):
        return self.repo.features(self.ref, self.path)

    @property
    def featuretype(self):
        return self.repo.featuretype(self.ref, self.path)

    @property
    def children(self):
        return self.repo.children(self.ref, self.path)

    @property
    def count(self):
        return self.repo.count(self.ref, self.path)

    def exportshp(self, shapefile):
        '''exports this tree to the specified shapefile'''
        self.repo.exportshp(self.ref, self.path, shapefile)

    def __str__(self):
        return self.ref + ":" + self.path
