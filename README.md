# lingtypology
<table>
  <tr>
    <td>Latest Release</td>
    <td>
      <a href="https://pypi.org/project/lingtypology/"/>
      <img src="https://img.shields.io/pypi/v/lingtypology.svg"/>
    </td>
  </tr>
  <tr>
    <td> Build Status </td>
    <td>
      <a href="https://travis-ci.org/OneAdder/lingtypology"/>
      <img src="https://img.shields.io/travis/OneAdder/lingtypology.svg"/>
    </td>
  </tr>
  <tr>
    <td>Code Quality</td>
    <td>
      <a href="https://app.codacy.com/app/OneAdder/lingtypology?utm_source=github.com&utm_medium=referral&utm_content=OneAdder/lingtypology&utm_campaign=Badge_Grade_Dashboard"/>
      <img src="https://api.codacy.com/project/badge/Grade/abe7b99539d141c4acbd3b485fd80959"/>
    </td>
  </tr>
  <tr>
    <td>License</td>
    <td>
      <a href="https://github.com/OneAdder/lingtypology/blob/master/LICENSE.md"/>
      <img src="https://img.shields.io/github/license/OneAdder/lingtypology.svg"/>
    </td>
  </tr>
  <tr>
    <td>DOI</td>
    <td>
      <a href="https://doi.org/10.5281/zenodo.2669068"/>
      <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.2669068.svg"/>
    </td>
  </tr>
</table>

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
For more informations consult the [tutorial](https://oneadder.github.io/lingtypology/)
or docstrings from the code.

## Glottolog
Lingtypology relies on data from the [Glottolog](https://glottolog.org/glottolog/language) database.
With each new version of `lingtypology` Glottolog data is updated. Now it is using Glottolog `3.4-34`.
You can update data from Glottolog. To get the instruction on how to do it, consult the [tutorial](https://oneadder.github.io/lingtypology/glottolog#g_version).

## Citation
If you are using this package in a scientific publication, it will be most appreciated if you add the citation:
```
@misc{MichaelVoronov2669068,
    author = {Michael Voronov},
    title = {{lingtypology: a Python tool for linguistic typology}},
    month = june,
    year = 2019,
    doi = {10.5281/zenodo.2669068},
    url = {https://doi.org/10.5281/zenodo.2669068}
}
```
