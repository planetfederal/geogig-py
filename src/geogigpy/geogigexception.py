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
    