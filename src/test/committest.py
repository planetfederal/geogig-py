# -*- coding: utf-8 -*-

"""
***************************************************************************
    committest.py
    ---------------------
    Date                 : January 2014
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
__date__ = 'January 2014'
__copyright__ = '(C) 2014-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import unittest
import os
import time
from geogigpy.commit import Commit
from testrepo import testRepo


class GeogigCommitTest(unittest.TestCase):

    repo = testRepo()

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        dst = self.getTempPath()
        return self.repo.clone(dst)

    def testFromRef(self):
        ref = self.repo.head.ref
        commit = Commit.fromref(self.repo, ref)
        log = self.repo.log()
        headcommit = log[0]
        self.assertEqual(headcommit.ref, commit.ref)
        self.assertEqual(headcommit.committerdate, commit.committerdate)

    def testCommitDiff(self):
        log = self.repo.log()
        commit = log[0]
        diff = commit.diff()
        self.assertEquals(1, len(diff))
        self.assertEquals("parks/5", diff[0].path)
