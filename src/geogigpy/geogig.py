# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
    ---------------------
    Date                 : August 2014
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
__date__ = 'August 2014'
__copyright__ = '(C) 2014-2016 Boundless, http://boundlessgeo.com'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


MASTER = 'master'
HEAD = 'HEAD'
WORK_HEAD = 'WORK_HEAD'
STAGE_HEAD = 'STAGE_HEAD'

RESET_MODE_HARD = "hard"
RESET_MODE_MIXED = "mixed"
RESET_MODE_SOFT = "soft"

NULL_ID = "0" * 40

TYPE_BOOLEAN = "BOOLEAN"
TYPE_BYTE = "BYTE"
TYPE_SHORT = "SHORT"
TYPE_INTEGER = "INTEGER"
TYPE_LONG = "LONG"
TYPE_FLOAT = "FLOAT"
TYPE_DOUBLE = "DOUBLE"
TYPE_POINT = "POINT"
TYPE_LINESTRING = "LINESTRING"
TYPE_POLYGON = "POINT"
TYPE_MULTIPOINT = "MULTIPOINT"
TYPE_MULTILINESTRING = "MULTILINESTRING"
TYPE_MULTIPOLYGON = "MULTIPOLYGON"
TYPE_STRING = "STRING"

GEOMTYPES = [TYPE_MULTIPOINT, TYPE_MULTILINESTRING, TYPE_POLYGON,
             TYPE_POINT, TYPE_LINESTRING, TYPE_MULTIPOLYGON]

USER_NAME = "user.name"
USER_EMAIL = "user.email"
STORAGE_OBJECTS = "storage.objects"
MONGODB = "mongodb"
STORAGE_GRAPH = "storage.graph"
STORAGE_STAGING = "storage.staging"
MONGODB_VERSION = "mongodb.version"

OURS = "ours"
THEIRS = "theirs"

ORIGIN = "origin"
