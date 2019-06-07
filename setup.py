# -*- coding: utf-8 -*-
"""
# lingtypology
Lingtypology is a Python3 tool for linguistic interactive mapping and online linguistic databases API.
It is inspired by [R-package](https://github.com/ropensci/lingtypology) created by [Agrizolamz](https://github.com/agricolamz).
It uses the same phylosophy and provides similar functionality.  

## Installation
The package is available in PyPI.
Therefore, you can install it by running:  
Locally: `pip3 install lingtypology --user`  
Globally (not recommended): `sudo pip3 install lingtypology`

## Usage
Lingtypology package contains `LingMap` class that allows to draw interactive maps, `glottolog` library that allows to interact with Glottolog data and `db_apis` that allows to interact with different other linguistic databases.  
For more informations consult the [tutorial](https://oneadder.github.io/lingtypology/).
"""
from setuptools import setup
from lingtypology import __version__

setup(
    name='lingtypology',
    version=__version__,
    description='A tool for linguistic typology.',
    long_description=__doc__,
    long_description_content_type='text/markdown',
    url='https://github.com/OneAdder/lingtypology',
    author='Michael Voronov',
    author_email='mikivo@list.ru',
    license='GPLv3',
    packages=['lingtypology'],
    python_requires='>=3.5',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
          'folium',
          'branca',
          'jinja2',
          'pandas',
          'pyglottolog',
          'colour',
          'matplotlib',
          'selenium'
    ],
    extras_require={
        'test': [
            'pytest>=3.6',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Text Processing :: Linguistic',
    ],
) 
