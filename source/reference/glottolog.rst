.. _glottolog:

``lingtypology.glottolog``
===========================

.. _functions-1:

Functions
~~~~~~~~~

Glottolog module includes various functions to work with Glottolog data.

The only funcntion that accepts list-like objects and returns *list* is
**get_affiliations**. Its **parameter** is language names, it
**returns** the genealogical information for the given languages.

The **parameter** of all the other functions is *str* and they
**return** *str*.

The following functions use language name as the **parameter** and
**return** coordinates, Glottocode, macro area and ISO code
respectively:

-  lingtypology.glottolog.\ **get_coordinates**

-  lingtypology.glottolog.\ **get_glot_id**

-  lingtypology.glottolog.\ **get_macroarea**

-  lingtypology.glottolog.\ **get_iso**

The following functions use Glottocode as the **parameter** and
**return** coordinates, language name and ISO code respectively:

-  lingtypology.glottolog.\ **get_coordinates_by_glot_id**

-  lingtypology.glottolog.\ **get_by_glot_id**

-  lingtypology.glottolog.\ **get_iso_by_glot_id**

The following functions use ISO code as the **parameter** and **return**
language name and Glottocode respectively.

-  lingtypology.glottolog.\ **get_by_iso**

-  lingtypology.glottolog.\ **get_glot_id_by_iso**

Versions
~~~~~~~~

Processed Glottolog data is stored statically in the package directory.
It is updated with each new release of ``lingtypology``.

The version of the Glottolog data which is currently used is stored in
lingtypology.glottolog.\ **version** variable.

It is possible to use local Glottolog data. To do so, it is necessary to
perform the following steps:

-  Download the current version of the Glottolog data.

-  Create directory ``.lingtypology_data`` in your home directory.

-  Move ``glottolog`` to ``.lingtypology_data``.

-  Run the following command:

.. code-block:: shell

    glottolog –repos=glottolog languoids

-  It will generate two small files (``csv`` and ``json``). Now you can delete
   everything except for these files from the directory.

-  LingTypology will automatically use the local data.
