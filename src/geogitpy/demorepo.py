import shapefile
from repo import Repository
import random

def importAndCommit(repo, shp, message):
	repo.importshp(shp)
	repo.add()
	repo.

def createSampleTestRepo(path):
	repo = Repository(path, init = true)
	shp = createLineShapefile()
	createCommits(shp, repo, 500)


def createCommits():
	importandcommit(shp)
	modifyGeometries(shp)
	importAndCommit(shp)
	modifyAttributes(shp)

def modifyGeometries(shp):
	
