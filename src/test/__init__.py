# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : April 2014
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
__date__ = 'April 2014'
__copyright__ = '(C) 2014-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import unittest
from treetest import GeogigTreeTest
from testrepo import testRepo
from repotest import GeogigRepositoryTest
from featuretest import GeogigFeatureTest
from commitishtest import GeogigCommitishTest
from committest import GeogigCommitTest
from difftest import GeogigDiffTest


def suite():
    suite = unittest.makeSuite(GeogigTreeTest, 'test')
    suite.addTests(unittest.makeSuite(GeogigRepositoryTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogigFeatureTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogigCommitishTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogigCommitTest, 'test'))
    suite.addTests(unittest.makeSuite(GeogigDiffTest, 'test'))
    return suite
