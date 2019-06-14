.. LingTypology documentation master file, created by
   sphinx-quickstart on Wed Jun 12 21:21:05 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

LingTypology: Documentation
========================================

Lingtypology is a Python3 tool for linguistic interactive mapping and
online linguistic databases API. It is inspired by
`R-package <https://github.com/ropensci/lingtypology>`__ created by
`Agrizolamz <https://github.com/agricolamz>`__. It uses the same
phylosophy and provides similar functionality.

`Gihub Repository <https://github.com/OneAdder/lingtypology>`_,
`PyPI <https://pypi.org/project/lingtypology/>`_,
`DOI <https://doi.org/10.5281/zenodo.2669068>`_,
`License <https://github.com/OneAdder/lingtypology/blob/master/LICENSE.md>`_

Installation
------------

The package is available in PyPI. Therefore, you can install it by running:

Locally: 

.. code-block:: shell

    pip3 install lingtypology --user

Globally (not recommended):

.. code-block:: shell

    sudo pip3 install lingtypology

Usage
-----

Lingtypology package contains ``LingMap`` class that allows to draw
interactive maps, ``glottolog`` library that allows to interact with
Glottolog data and ``datasets`` that allows to interact with different
online linguistic databases.

Contents
========

Tutorial
--------
.. toctree::
    :maxdepth: 3
    
    tutorial/t_maps
    tutorial/t_datasets

Reference Manual
----------------
.. toctree::
    :maxdepth: 3
    
    reference/maps
    reference/datasets
    reference/glottolog


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
