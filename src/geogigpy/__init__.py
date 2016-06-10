# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
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

from geogig import *
from repo import Repository
from commitish import Commitish
from feature import Feature
from tree import Tree
from diff import Diffentry
from commit import Commit

__version__ = "1.1-SNAPSHOT"
