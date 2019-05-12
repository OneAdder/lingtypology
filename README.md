# lingtypology
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2770756.svg)](https://doi.org/10.5281/zenodo.2770756)  
This library is a Python3 tool for linguistic interactive mapping.
It is inspired by [R-package](https://github.com/ropensci/lingtypology) created by [Agrizolamz](https://github.com/agricolamz).
It uses the same phylosophy and provides similar functionality.  

## Installation
The package is available in PyPI.
Therefore, you can install it by running:  
Locally: `pip3 install lingtypology --user`  
Globally (not recommended): `sudo pip3 install lingtypology`

## Usage
Lingtypology package contains `LingMap` class that allows to draw interactive maps, `glottolog` library that allows to interact with Glottolog data and `db_apis` that allows to interact with different other linguistic databases.  
For more informations consult the [tutorial](https://oneadder.github.io/lingtypology/)
or docstrings from the code.

## Glottolog
Lingtypology relies on data from the [Glottolog](https://glottolog.org/glottolog/language) database.
With each new version of `lingtypology` Glottolog data is updated. Now it is using Glottolog `3.4-16`.
You can update data from Glottolog. To get the instruction on how to do it, consult the [tutorial](https://oneadder.github.io/lingtypology/glottolog#g_version).

## Citation
If you are using this package in a scientific publication, it will be most appreciated if you add the citation:
```
@misc{michael_voronov_2019_2770756,
author       = {Michael Voronov},
title        = {{lingtypology: a Python tool for linguistic interactive mapping}},
month        = may,
year         = 2019,
doi          = {10.5281/zenodo.2770756},
url          = {https://doi.org/10.5281/zenodo.2770756}
}
```
