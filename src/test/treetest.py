# -*- coding: utf-8 -*-

"""
***************************************************************************
    treetest.py
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


import unittest
import os
import time
from geogigpy.tree import Tree
from geogigpy import geogig
from testrepo import testRepo


class GeogigTreeTest(unittest.TestCase):

    repo = testRepo()

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        dst = self.getTempPath()
        return self.repo.clone(dst)

    def testExportShp(self):
        repo = self.getClonedRepo()
        exportPath = os.path.join(os.path.dirname(__file__), "temp", str(time.time()) + ".shp").replace('\\', '/')
        tree = Tree(repo, geogig.HEAD, "parks")
        tree.exportshp(exportPath)
        self.assertTrue(os.path.exists(exportPath))

    def testFeatures(self):
        tree = Tree(self.repo, geogig.HEAD, "parks")
        features = tree.features
        self.assertEquals(5, len(features))

    def testFeatureType(self):
        tree = Tree(self.repo, geogig.HEAD, "parks")
        ftype = tree.featuretype
        self.assertEqual("DOUBLE", ftype["perimeter"])
        self.assertEqual("STRING", ftype["name"])
        self.assertEqual("MULTIPOLYGON", ftype["the_geom"])
