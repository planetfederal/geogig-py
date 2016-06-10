# -*- coding: utf-8 -*-

"""
***************************************************************************
    osmmapping.py
    ---------------------
    Date                 : December 2013
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
__date__ = 'December 2013'
__copyright__ = '(C) 2013-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import json


class OSMMappingRule(object):

    def __init__(self, name):
        self.name = name
        self.fields = {}
        self.filter = {}
        self.exclude = {}

    def addfield(self, tagname, fieldname, fieldtype):
        d = {"name": fieldname, "type": fieldtype}
        self.fields[tagname] = d

    def addfilter(self, name, *tags):
        self.filter[name] = tags

    def addexclusion(self, name, *tags):
        self.filter[name] = tags

    def asjson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)


class OSMMapping(object):

    def __init__(self):
        self.rules = []

    def addrule(self, rule):
        self.rules.append(rule)

    def asjson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)
