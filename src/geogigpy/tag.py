# -*- coding: utf-8 -*-

"""
***************************************************************************
    tag.py
    ---------------------
    Date                 : January 2015
    Copyright            : (C) 2015-2016 Boundless, http://boundlessgeo.com
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
__date__ = 'January 2015'
__copyright__ = '(C) 2015-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from commit import Commit


class Tag(object):
    '''An object representing a tag'''

    ROOT = None

    def __init__(self, repo, tagid, name):
        self.repo = repo
        self.tagid = tagid
        self.name = name
        self._commit = None

    @property
    def commit(self):
        if self._commit is None:
            lines = self.repo.connector.cat(self.tagid).split("\n")
            commitid = lines[3][-40:]
            self._commit = Commit.fromref(self.repo, commitid)
        return self._commit

    def __str__(self):
        return self.name + ":" + self.tagid
