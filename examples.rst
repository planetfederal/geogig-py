Examples
*********

The following are some examples about using the geogit-py library.

Notice that these scripts are not optimized (using them in very large repositories might not work correctly and a ifferent approach should be implemented) and can be improved in terms of robustness. They are provided here just to illustrate some standard usage of geogit-py for scripting GeoGit tasks.


Squashing the latest *n* commits
------------------------------------------

The following method squashes the latest *n* commits in the current history

::

	import geogit
	from geogitpy.commit import Commit

	def squash_latest(repo, n, message = None):
	    '''
	    Squashes the latest n commits into a single one.
	    If a message is passed, it uses it for the resulting commit.
	    Otherwise, it uses the messages from the squashed commits
	    ''' 
	    if n < 1:
	        raise Exception("Cannot squash less than 2 commits")    
	    log = repo.log()
	    if len(log) < n:
	        raise Exception("Not enough commits in history")        
	    message = message or "\n".join([commit.message for commit in log[:n]])
	    repo.reset(log[n].ref, geogit.RESET_MODE_MIXED)
	    repo.add()
	    repo.commit(message)

If instead of the n latest commits, we want to squash all commits between two given ones, the following function can be used:
    
::

	def squash(repo, refa, refb, message = None):
	    '''
	    Squashes all the commits between two given ones, 'refa' and 'refb'.
	    Commits are passed as a string with the correspoding commit id
	    If a message is passed, it uses it for the resulting commit.
	    Otherwise, it uses the messages from the squashed commits
	    '''
	    head = repo.head
	    
	    commita = Commit.fromref(repo, refa);
	    commitb = Commit.fromref(repo, refb);    
	    
	    # check that commmits are in the correct order 
	    # (a older than b) and swap them otherwise
	    if commita.committerdate > commitb.committerdate:
	        refa, refb = refb, refa
	        commita, commitb = commitb, commita
	        
	    # store the commits after the last one to squash
	    commits = []
	    c = head
	    commitid = c.id   
	    while commitid != refb:
	        commits.append(commitid)
	        c = c.parent
	        commitid = c.id  
	                
	    # squash the selected commmits        
	    repo.reset(refb, geogit.RESET_MODE_HARD)
	    repo.reset(commita.parent.id, geogit.RESET_MODE_MIXED)
	    
	    if message is None:
	        messages = []
	        c = commitb
	        messages.append(c.message)
	        while c.ref != refa:
	            c = c.parent
	            messages.append(c.message)	            
	        message = "+".join(messages)

	    repo.add()
	    repo.commit(message)
	    
	    # and now add the remaining commits that we previously stored      
	    for c in reversed(commits):
	        repo.cherrypick(c)
            
The above method can be used like this:

::

    >>> repo = Repository('my/path/to/repository')
    >>> log = repo.log()
    >>> print len(log)
    4
    >>> squash(repo, log[2].ref, log[1].ref)
    >>> log = repo.log()
    >>> print len(log)
    3
    >>>print log[0].message
    message_4
    >>>print log[1].message
    message_3+message_2


Note: both methods described above assume that the history of the repository is linear and does not contains branches that have been merged in the commits to be merged or those after them. A more general solution would require a different and more complex approach. Once again, they are provided just as an example.


List of the last author to modify each tree 
--------------------------------------------

::

	def blame_tree(repo):
	    '''
	    Returns a dict with tree names ids as keys and the name of the last 
	    person to edit each tree as values
	    '''
	    authors = {}    
	    for tree in repo.trees:
	        path = tree.path
	        log = repo.log(path, n = 1)
	        authors[path] = log[0].authorname 
	    return authors
	            

Exporting all trees to a single PostGIS database
------------------------------------------------

It creates a table for each tree in the repository, using the name of the tree as name of the table.

::

	def export_to_pg(repo, host, user, password, port, database, schema = "public"):
	    for tree in repo.trees:
	        path = tree.path
	        repo.exportpg(geogit.HEAD, path, path, database, user, password, schema, host, port)
    

Importing all shapefiles in a folder
------------------------------------

The following method imports all shapefiles in a folder into a repository

::

	import os
	
	def import_folder(repo, folder):		
		for f in os.listdir(folder):
    		if f.endswith(".shp"):
    	path = os.path.join(folder, f)
        repo.importshp(path)

If you want to allow importing all shapefiles into a single destination tree ``dest`` instead of importing each one into a different tree (with a name assigned automatically by GeoGit based on the filename), you can improve the above function like this.

::

	import os
	
	def import_folder(repo, folder, dest = None):		
		for f in os.listdir(folder):
    		if f.endswith(".shp"):
    	path = os.path.join(folder, f)
        repo.importshp(path, dest = dest)

And here is a more complex example, in which shapefiles are assumed to be in subfolders and all the files in a subfolder are imported to a tree with the name of the subfolder itself. It also creates a commit for each folder after importing, adding some extra information in the commit message.

::

	import os

	def import_subfolders_and_commit(repo, folder, dest = None):		
		for p in os.listdir(folder):
    		if os.path.isdir(p):
    			subfolder = os.path.join(folder, p)
    			n = 0
    			for f in os.listdir(subfolder):
    				if f.endswith(".shp"):
    					path = os.path.join(folder, f)
        				repo.importshp(path, dest = dest)
        		if n:
	        		diffs = repo.difftreestats()        
	        		total = sum(diffs.iterator().next())	        		
	        		message = "Imported %s. %i features imported. %i features modified" % (p, n, total)
	        		repo.addandcommit(message)


A simple GeoGit workflow
--------------------------

::

	# Crate repo
	repo = Repository('path/to/repo/folder', True)

	# Configure
	repo.config(geogit.USER_NAME, 'myuser')
	repo.config(geogit.USER_EMAIL, 'myuser@mymail.com')

	# Add some data and create a snapshot
	repo.importshp('myshapefile.shp')
	repo.addandcommit('first import')	
	
	# Create a branch to work on it
	repo.createbranch(repo.head, "mybranch", checkout = True)
	
	# Take a feature and modify its geometry
	feature = repo.feature(geogit.HEAD, 'parks/1')		
	geom = feature.geom
	attributes = feature.attributesnogeom
	newgeom = geom.buffer(5.0)

	# insert the modified geometry and create a new snapshot with the changes
	repo.insertfeature(feature.path, attributes, newgeom)
	repo.addandcommit("modified parks/1 (buffer computed)")

	# Bring changes to master branch
	# [...] There might be changes in the master branch as well

	repo.checkout(geogit.MASTER)
	try:
		repo.merge("mybranch")
		print "No merge conflicts"
	except GeoGitConflictException, e:
		print "There are merge conflicts"
