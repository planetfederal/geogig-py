# -*- coding: utf-8 -*-

"""
***************************************************************************
    diff.py
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


from feature import Feature
from geogig import NULL_ID

TYPE_MODIFIED = "Modified"
TYPE_ADDED = "Added"
TYPE_REMOVED = "Removed"

ATTRIBUTE_DIFF_MODIFIED, ATTRIBUTE_DIFF_ADDED, ATTRIBUTE_DIFF_REMOVED, ATTRIBUTE_DIFF_UNCHANGED = ["M", "A", "R", "U"]


class Diffentry(object):

    '''A difference between two references for a given path'''

    def __init__(self, repo, oldcommitref, newcommitref, oldref, newref, path):
        self.repo = repo
        self.path = path
        self.oldref = oldref
        self.newref = newref
        self.oldcommitref = oldcommitref
        self.newcommitref = newcommitref

    def oldobject(self):
        if self.oldref == NULL_ID:
            return None
        else:
            return Feature(self.repo, self.oldcommitref, self.path)

    def newobject(self):
        if self.newref == NULL_ID:
            return None
        else:
            return Feature(self.repo, self.newcommitref, self.path)

    def featurediff(self):
        return self.repo.featurediff(self.oldcommitref, self.newcommitref, self.path)

    def type(self):
        if self.oldref == NULL_ID:
            return TYPE_ADDED
        elif self.newref == NULL_ID:
            return TYPE_REMOVED
        else:
            return TYPE_MODIFIED

    def __str__(self):
        if self.oldref == NULL_ID:
            return "%s %s (%s)" % (TYPE_ADDED, self.path, self.newref)
        elif self.newref == NULL_ID:
            return TYPE_REMOVED + " " + self.path
        else:
            return "%s %s (%s --> %s)" % (TYPE_MODIFIED, self.path, self.oldref, self.newref)
