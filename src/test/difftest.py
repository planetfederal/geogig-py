# -*- coding: utf-8 -*-

"""
***************************************************************************
    difftest.py
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
from testrepo import testRepo


class GeogigDiffTest(unittest.TestCase):

    repo = testRepo()

    def getTempPath(self):
        return os.path.join(os.path.dirname(__file__), "temp", str(time.time())).replace('\\', '/')

    def getClonedRepo(self):
        dst = self.getTempPath()
        return self.repo.clone(dst)

    def testOldFeatureIsNone(self):
        diff = self.repo.log()[0].diff()[0]
        old = diff.oldobject()
        self.assertIsNotNone(old)
        self.assertEquals("parks/5", old.path)
        attrs = old.attributes
        self.assertEqual(15297.503295898438, attrs['area'])

    def testNewFeature(self):
        diff = self.repo.log()[0].diff()[0]
        new = diff.newobject()
        self.assertIsNotNone(new)
        self.assertEquals("parks/5", new.path)
        attrs = new.attributes
        self.assertEqual(15246.59765625, attrs['area'])
