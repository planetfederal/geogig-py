geogigpy
========

A Python library to use GeoGig.

This library is designed to provide access to all GeoGig functionality, so it can be used to script tasks or as the base library for a GeoGig client.

Installation
-------------

To install, use ``pip`` or ``easy_install``:

::
	
	$ pip install geogig-py

or

::

	$ easy_install geogig-py

For developers wanting to improve or modify ``geogig-py``, you should clone the GitHub repo and then install the library in a virtual environment, following these steps

::

	$ git clone git://github.com/boundlessgeo/geogig-py.git 
	$ cd geogig-py 
	$ python setup.py develop (`virtualenv <http://virtualenv.org/>`_ of your choice)


GeoGig is not included with geogig-py, and it is assumed to be already installed in your system. Particularly, geogig-py assumes that the folder where GeoGig launch scripts are found is in your current PATH.

Usage
-----

Usage is described `here <./doc/source/usage.rst>`_.

Examples
--------

You can find `here <./doc/source/examples.rst>`_ some examples on how to use geogig-py for basic and more complex scripting tasks.

Testing
--------

To run unit tests, just run the ``test.py`` module in ``src/test``. Most of the tests are integration tests, but test data is included and the only requisite is to have GeoGig installed and correctly configured.


Architecture. Connectors
-------------------------

The ``repo`` object delegates most of its work to a connector, which communicates with a GeoGig instance. Currently there are two connectors available:

- A CLI-based connector, which uses the console to call the GeoGig command-line interface and parses its output. It assumes that GeoGig is installed in your system and available in your current PATH. Basically, if you open a console, type ``geogig`` and you get the GeoGig help, you are ready to use a ``geogigpy`` repository using the CLI connector. This is far from efficient, as it has to call GeoGig (and thus, start a JVM) each time an operation is performed.

- A Py4J-based connector, which communicates with a GeoGig gateway server. To start the server, you can run ``geogig-gateway`` on a console. If the server is not running and accepting GeoGig commands, the connector will try to start it. In this case, it will assume that, as in the case of running a CLI-based connector, GeoGig is installed and available in your current path. More specifically, the ``geogig-gateway`` script should be available.

If the server is not running and the ``geogig-gateway`` script is not available, you can set the path to the folder with GeoGig launch scripts using the ``setGeoGigPath`` function in the ``py4jconnector`` module.

::

	import py4jconnector
	py4jconnector.setGeoGigPath('path/to/geogig/scritps')	

By default, a ``Repository`` object uses a Py4J-based connector (without any path for GeoGig scripts, so it assumes they are in PATH) if no connector is passed.

