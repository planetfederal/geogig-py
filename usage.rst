Using the geogit-py library
*****************************

this documet describes the main ideas about using the goegit-py library

Most of the functionality is available through the ``Repository`` class.

Instantiate a repository passing its URL, and you will have all GeoGit commands available as methods of the ``Repository`` object

::

	>>> #create an empty repository
	>>> repo = Repository('path/to/repository/folder', init = True)
	>>> #import data
	>>> repo.importshp("/path/to/shp/file")
	>>> #add unstaged features
	>>> repo.add()
	>>> #commit
	>>> repo.commit(message = "a commit message")

Apart from this, geogit-py features an object-oriented approach, which allows you to deal with the objects of the repository in a different way. Here is an example.


You can create a repository object to use an existing repo and get the log of the repo
	
::

	>>> repo = Repository('path/to/repository/folder')
	>>> log = repo.log()
	
``log`` is a list of ``Commit`` object, which can be used to get the differences each commit introduces
	
::

	>>> print log[0]
	id 93880f09e919526008ff598ba86ee671b2b9594a
	parent 92863701fd6e8724331c012617dbea32136dcc4c
	tree cb6c689b61459e8adcb1a2ecc5d2d870908d83e9
	author volaya 2013-11-19 00:37:22
	message modified a feature        
	>>> print log[0].diff()
	Modified parks/4 (df86510c37ab884d9b80d660be4c235843049d1a --> 3632fc722cfdfae72a6694eced791586d1e6b1ba)
	Added parks/1 (6e2ded64426d5368fdb9017be867ee574f1c02cd)
	Added parks/2 (75a0cbf170714fb1b60f0bd80fddeac8fbfb2429)
	Added parks/3 (af4c5f499e22bdeed3081237d069fb515fd76c34) 
	
That was done on the current branch, but we can use other branches as well. Let's have a look at the history of branch "mybranch"    

::

	>>> branch = repo.branches['mybranch']
	>>> log = branch.log()   
	>>> print log[0]   	
	[...]    
	>>> print log[0].diff()
	[...]    
	

Let's explore the tree corresponding to the tip of that branch    

::

	>>> root = log[0].root

	
``root`` is a ``Tree`` object that points to the root tree in that snapshot. We can see the subtrees it contains.
	
::
	
	>>> for subtree in root.trees:
	>>>     print subtree
	parks
	roads
	
Each subtree is a ``Tree`` object itself, and we can see its trees and its features.

::
		
	>>> for feature in trees[0].features: 
	>>>     print feature
	parks/park1
	parks/park2
	parks/park3   
	
And we can see the attributes of a feature.

::
	
	>>> print tree[0].features[0].attributes        	
	{'open': True, 'name': 'Central park', 'area': 23876.5, "the_geom": MULTIPOLYGON (((-122.87290 42.335, ...

Geometries are Shapely objects, so you can use methods from the Shapely library to operate on them.

You can even add new elements to the repository, or modify existing ones.

::

	geom = tree[0].feeatures[0].attributes['the_geom']
	newattributes = {'open': False, 'name': 'New Central park', 'area': 23876.5}
	repo.modifyfeature("parks/parks1", newattributes, geom)

This sets the new feature in the working tree, with two attributes changed (*open* and *name*). Then you can add and commit as usual.

This way of editing/adding features only supports features with a single geometry attribute. If you need to insert a feature with several geometry attributes, you must manually export it to a format that supports it (i.e. a PostGIS database) and then import using the corresponding method

Failed operations and exceptions
================================

When a GeoGit operation exits with a non-zero exit code, geogit-py will raise a ``GeoGitException`` exception, containing the error message output by GeoGit as exception message. This will happen, for instance, if you do something like this

When GeoGit exist with a non-zero exit code, and it is not caused by an error but by a problem in the operation performed (such as, for instance, a conflicted merge), geogit-py will raise a ``InterruptedOperationException`` instead. That allows to differentiate between exceptions that are actually a problem, most likely related to the input parameters, from those that arise commonly in a normal GeoGit workflow and should be treated differently
