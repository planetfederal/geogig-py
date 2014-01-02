import os
from setuptools import setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="geogit-py",
    version="0.1.1",
    install_requires=['Shapely>=1.2.9', 'py4j>=0.8'],
    author="Victor Olaya",
    author_email="volaya@boundlessgeo.com",
    description="Python bindings for GeoGit",
    long_description=(read('README')),
    # Full list of classifiers can be found at:
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    license="BSD",
    keywords="geogit",
    url='https://github.com/boundlessgeo/geogit-py',
    package_dir={'': 'src'},
    packages=['geogitpy',]
)
