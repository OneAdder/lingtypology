# lingtypology
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2669069.svg)](https://doi.org/10.5281/zenodo.2669069)  
This library is a Python3 tool for linguistic interactive mapping.
It is based on [R-package](https://github.com/ropensci/lingtypology) created by [Agrizolamz](https://github.com/agricolamz).
It uses the same phylosophy and provides similar functionality.

## Installation
The package is available in PyPI.
Therefore, you can install it by running:  
Locally: `pip3 install lingtypology --user`  
Globally (not recommended): `sudo pip3 install lingtypology`

## Usage
Lingtypology package contains `LingMap` class that allows to draw interactive maps, `glottolog` library that allows to interact with Glottolog data and `db_apis` that allows to interact with different other linguistic databases.  
For more informations consult the tutorial
([html (Github pages)](https://oneadder.github.io/lingtypology/) or
[notebook](https://github.com/OneAdder/lingtypology/blob/master/docs/HOWTO.ipynb))
or docstrings from the code.

## Glottolog
Lingtypology relies on data from the [Glottolog](https://glottolog.org/glottolog/language) database.
With each new version of `lingtypology` Glottolog data is updated. Now it is using Glottolog `3.4-7`.
You can update data from Glottolog. To get the instruction on how to do it, consult paragraph 5.2 of the tutorial
([html (Github pages)](https://oneadder.github.io/lingtypology/#g_version) or
[notebook](https://github.com/OneAdder/lingtypology/blob/master/docs/HOWTO.ipynb))
