# -*- coding: utf-8 -*-

"""
***************************************************************************
    geogigexception.py
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


class GeoGigException(Exception):
    pass


class UnconfiguredUserException(Exception):
    pass


class InterruptedOperationException(Exception):
    '''
    An exception to signal an interrupted operation, not an actual error.
    To be used, for instance, for a merge/rebase process interrupted due to
    conflicts
    '''
    pass


class GeoGigConflictException(InterruptedOperationException):
    pass
