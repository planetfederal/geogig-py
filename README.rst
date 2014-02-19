geogitpy
========

A Python library to use GeoGit.

This library is designed to provide access to all GeoGit functionality, so it can be used to script tasks or as the base library for a GeoGit client.

Installation
-------------

To install, use ``pip`` or ``easy_install``

::
	
	$ pip install geogit-py

or

::

	$ easy_install geogit-py

For developers wanting to improve or modify ``geogit-py``, you should clone the GitHub repo and then install the library in a virtual environment, following these steps

::

	$ git clone git://github.com/boundlessgeo/geogit-py.git 
	$ cd geogit-py 
	$ python setup.py develop (`virtualenv <http://virtualenv.org/>`_ of your choice)


GeoGit is not included with geogit-py, and it is assumed to be already installed in your system. Particularly, geogit-py assumes that the folder where GeoGit launch scripts are found is in your current PATH.

Usage
-----

Usage is described `here <./doc/source/usage.rst>`_

Examples
--------

You can find `here <./doc/source/examples.rst>`_ some examples on how to use geogit-py for basic and more complex scripting tasks.

Testing
--------

To run unit tests, just run the ``test.py`` module in ``src/test``. Most of the tests are integration tests, but test data is included and the only requisite is to have GeoGit installed and correctly configured.


Architecture. Connectors
-------------------------

The ``repo`` object delegates most of its work to a connector, which communicates with a GeoGit instance. Currently there are two on connectors available:

- A CLI-based connector, which uses the console to call the GeoGit comand-line interface and parses its output. It assumes that GeoGit is installed in your system and available in your current PATH. Basically, if you open a console, type ``geogit`` and you get the GeoGit help, you are ready to use a ``geogitpy`` repository using the CLI connector. This is far from efficient, as it has to call GeoGit (and thus, start a JVM) each time an operation is performed. 

- A Py4J-based connector, which communicates with a GeoGit gateway server. To start the server, you can run ``geogit-gateway`` on a console. If the server is not running and accepting GeoGit commands, the connector will try to start it. In this case, it will assume that, as in the case of running a CLI-based connector, GeoGit is installed and available in your current path. More specifically, the ``geogit-gateway`` script should be available.

If the server is not running and the ``geogit-gateway`` script is not available, you can set the path to the folder with GeoGit launch scripts using the ``setGeoGitPath`` function in the ``py4jconnector`` module.

::

	import py4jconnector
	py4jconnector.setGeoGitPath('path/to/geogit/scritps')	

By default, a ``Repository`` object uses a Py4J-based connector (without any path for GeoGit scripts, so it assumes they are in PATH) if no connector is passed.

