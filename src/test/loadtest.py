# -*- coding: utf-8 -*-

"""
***************************************************************************
    loadtest.py
    ---------------------
    Date                 : March 2014
    Copyright            : (C) 2014-2016 Boundless, http://boundlessgeo.com
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
__date__ = 'March 2014'
__copyright__ = '(C) 2014-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import time
from geogigpy.repo import Repository
import unittest


class GeogigLoadTest(unittest.TestCase):

    def getTempRepoPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def testLargeDiff(self):
        repo = Repository(self.getTempRepoPath(), init=True)
        path = os.path.join(os.path.dirname(__file__), "data", "shp", "1", "parks.shp")
        repo.importshp(path)
        repo.addandcommit("message")
        path = os.path.join(os.path.dirname(__file__), "data", "shp", "elevation", "elevation.shp")
        repo.importshp(path)
        repo.addandcommit("message_2")
        s = repo.diff("HEAD~1", "HEAD")

    def testLargeHistory(self):
        NUMPOINTS = 6000
        repo = Repository(self.getTempRepoPath(), init=True)
        path = os.path.join(os.path.dirname(__file__), "data", "shp", "elevation", "elevation.shp")
        repo.importshp(path)
        repo.add()
        for i in xrange(NUMPOINTS):
            feature = "elevation/" + str(i + 1)
            message = "message " + str(i + 1)
            repo.commit(message, [feature])
        log = repo.log()
