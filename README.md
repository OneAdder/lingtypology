# lingtypology
This library is a Python3 tool for linguistic interactive mapping.
It is based on [R-package](https://github.com/ropensci/lingtypology) created by [Agrizolamz](https://github.com/agricolamz).
It uses the same phylosophy and provides similar functionality.

# Glottolog
Lingtypology relies on data from the [Glottolog](https://glottolog.org/glottolog/language) database.
With each new version of `lingtypology` Glottolog data is updated. Now it is using Glottolog `3.4-7`.
You can update data from Glottolog by using `lingtypology.update_glottolog()` function. However, it is buggy and not recommended yet.

# Installation
The package is available in PyPI.
Therefore, you can install it by running:  
Locally: `pip3 install lingtypology --user`  
Globally (not recommended): `sudo pip3 install lingtypology`

# Usage
Lingtypology package contains `LingMap` class that allows to draw interactive maps, `glottolog` library that allows to interact with Glottolog data and `db_apis` that allows to interact with different other linguistic databases.  
For more informations consult the [tutorial](https://github.com/OneAdder/lingtypology/blob/master/HOWTO.html) or docstrings from the code.
