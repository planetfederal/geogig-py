import os
from distutils.core import setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name="geogit",
    version="0.1",
    requires=['Python (>=2.6)', 'Shapely (>=1.3.0)'],
    author="",
    author_email="",
    description="Python bindings for GeoGit",
    long_description=(read('README')),
    # Full list of classifiers can be found at:
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - Planning',
    ],
    license="BSD",
    keywords="geogit",
    url='https://github.com/boundlessgeo/geogitpy',
    package_dir={'': 'src'},
    packages=['geogit',],
    include_package_data=True,
    zip_safe=False,
)
