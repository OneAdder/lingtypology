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

.. image:: https://img.shields.io/github/release/OneAdder/lingtypology.svg
    :target: https://github.com/OneAdder/lingtypology

.. image:: https://img.shields.io/pypi/v/lingtypology.svg
    :target: https://pypi.org/project/lingtypology/

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.3244114.svg
   :target: https://doi.org/10.5281/zenodo.3244114

.. image:: https://img.shields.io/github/license/OneAdder/lingtypology.svg
    :target: https://github.com/OneAdder/lingtypology/blob/master/LICENSE.md

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
online linguistic databases. See more info below.

Citation
---------
It would be most appreciated if you cite the package if you are using it. The suggested way is:

.. code-block:: bibtex

    @misc{MichaelVoronov2669068,
        author = {Michael Voronov},
        title = {{lingtypology: a Python tool for linguistic typology}},
        month = june,
        year = 2019,
        doi = {10.5281/zenodo.2669068},
        url = {https://doi.org/10.5281/zenodo.2669068}
    }

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
