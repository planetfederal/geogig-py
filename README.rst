geogitpy
========

A Python library to use GeoGit.

This library is designed to provide access to all GeoGit functionality, so it can be used to script tasks or as the base library for a GeoGit client.

Installation
-------------

``geogitpy`` assumes that GeoGit is installed in your system and available in your current PATH. Basically, if you open a console, type ``geogit`` and you get the GeoGit help, you are ready to use geogit.

The `Shapely <https://pypi.python.org/pypi/Shapely>`_ library is required for handling geometries and should be present in your PYTHONPATH.

Usage
-----

Most of the functionality is available through the ``Repository`` class.

Instantiate a repository passing its URL, and you will have all commands available as method of the ``Repository`` object

::

	>>> #create an empty repository
	>>> repo = Repository('path/to/repository/folder', init = true)
	>>> #import data
	>>> repo.importshp("/path/to/shp/file")
	>>> #add unstaged features
	>>> repo.add()
	>>> #commit
	>>> repo.commit(message = "a commit message")

Apart from this, geogitpy features an object-oriented approach, which allows you to deal with the objects of the repository in a different way. Here is an example.


You can create a repository object to use an existing repo and get the log of the repo
	
::

	>>> repo = Repository('path/to/repository/folder')
	>>> log = repo.log()
	
``log`` is a list of ``Commit`` object, which can be used to get the differences it introduces
	
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

	>>> branch = repo.branch('my_branch_name')
	>>> log = branch.log()   
	>>> print log[0]   	
	[...]    
	>>> print log[0].diff()
	[...]    
	

Let's explore the tree corresponding to the tip of that branch    

::

	>>> root = log[0].root()

	
``root`` is a ``Tree`` object that points to the root tree in that snapshot. We can see the subtrees it contains.
	
::

	>>> trees = root.trees()
	>>> for subtree in trees:
	>>>     print subtree
	parks
	roads
	
Each subtree is a ``Tree`` object itself, and we can see its trees and its features.

::
	
	>>> features = trees[0].features()
	>>> for feature in features:        
	>>>     print feature
	parks/park1
	parks/park2
	parks/park3   
	
And we can see the attributes of a feature.

::
	
	>>> attrs = features[0].attributes()        
	>>> print attrs
	{'open': True, 'name': 'Central park', 'area': 23876.5, "the_geom": MULTIPOLYGON (((-122.87290 42.335, ...

Geometries are Shapely objects, so you can use methods from the Shapely library to operate on them.

You can even add new elements to the repository, or modify existing ones.

::

	newattributes = {'open': False, 'name': 'New Central park', 'area': 23876.5, "the_geom": geom}
	repo.modifyfeature("parks/parks1", newattributes)

This sets the new feature in the working tree and then you can add and commit as usual.

Testing
--------

To run unit tests, just run the ``test.py`` module in ``src/test``. Most of the tests are integration tests, but test data is included and the only requisite is to have GeoGit installed and correctly configured as explained above.


Architecture
-------------

The ``repo`` object delegates most of its work to a connector, which communicates with a GeoGit instance. Currently there is only on connector available which uses the console to call the GeoGit comand-line interface and parses its output. This is far from efficient, as it has to call GeoGit (and thus, start a JVM) each time an operation is performed. Alternative connectors based on the GeoGit server API, or that use additional libraries to keep a JVM instance running, are currently being developed.
