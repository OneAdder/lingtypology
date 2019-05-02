"""Using data from Glottolog DB"""
import pandas
import os
from pathlib import Path

def get_glottolog_table(directory):
    """get name of the CSV and version

    This function returns name and version of the proper CSV-file containing Glottolog data.
    glottolog utility from pyglottolog package creates the CSV table and names it:
    glottolog-languoids-pyglottolog-[version-version-version].csv
    """
    table_name = [file for file in os.listdir(directory) if file.startswith('glottolog-languoids') and file.endswith('.csv')][0]
    version = '-'.join(table_name.split('-')[-3:])[:-4]
    path = os.path.join(directory, table_name)
    return path, version
    
#---------------------------------------------------------------------------------
home = Path.home()
try:
    path, version = get_glottolog_table(os.path.join(str(home), '.lingtypology_data'))
except (FileNotFoundError, IndexError):
    module_directory = os.path.dirname(os.path.realpath(__file__))
    path, version = get_glottolog_table(module_directory)

glottolog = pandas.read_csv(path, delimiter=',', header=0)
warnings = []
#---------------------------------------------------------------------------------


def get_affiliations(languages):
    """
    get_affiliations(('Russian', 'English'))
    >>> ['Indo-European, Balto-Slavic, Slavic, East Slavic', 'Indo-European, ...']
    """
    affiliations = []
    for language in languages:
        affiliation_id = tuple(glottolog[glottolog.Name == language].Classification)
        if not affiliation_id:
            affiliation = ''
            print('(get_affiliations) Warning: affiliation for {} not found'.format(language))
        else:
            affiliation = []
            affiliation_id = affiliation_id[0].split('/')
            for taxon in affiliation_id:
                affiliation.append(tuple(glottolog[glottolog.ID == taxon].Name)[0])
            affiliation = ', '.join(affiliation)
        affiliations.append(affiliation)
    return affiliations


def get_coordinates(language):
    """
    get_coordinates('Russian')
    >>> (59.0, 50.0)
    """
    latitude = glottolog[glottolog.Name == language].Latitude
    longitude = glottolog[glottolog.Name == language].Longitude
    if not list(latitude) or not list(longitude):
        global warnings
        warnings.append(language)
        #print('(get_coordinates) Warning: coordinates for {} not found'.format(language))
    else:
        return (float(latitude), float(longitude))


def get_glot_id(language):
    """
    get_glot_id('Russian')
    >>> russ1263
    """
    glot_id = tuple(glottolog[glottolog.Name == language].ID)
    if not glot_id:
        pass
        #print('(get_glot_id) Warning: Glottolog ID for {} not found'.format(language))
    else:
        return glot_id[0]


def get_macro_area(language):
    """
    get_macro_area('Russian')
    >>> Eurasia
    """
    macro_area = tuple(glottolog[glottolog.Name == language].Macroarea)
    if not macro_area:
        print('(get_macro_area) Warning: Macro area for {} not found'.format(language))
    else:
        return macro_area[0]



def get_iso(language):
    """
    get_iso('Russian')
    >>> rus
    """
    iso = tuple(glottolog[glottolog.Name == language].ISO639P3code)
    if not iso:
        print('(get_iso) Warning: ISO for {} not found'.format(language))
    else:
        return iso[0]

#---------------------------------------------------------------------------------

'''
get_by_affiliation('Indo-European, Slavic, East')
>>> ('Ukrainian', 'Rusyn', 'Russian', 'Belarusian')
def get_by_affiliation(affiliation):
    languages = tuple(glottolog[glottolog.affiliation == affiliation].language)
    if not languages:
        print('(get_by_affiliation) Warning: languages by {} not found'.format(affiliation))
    else:
        return languages
'''


def get_by_iso(iso):
    """
    get_by_iso('rus')
    >>> Russian
    """
    language = tuple(glottolog[glottolog.ISO639P3code == iso].Name)
    if not language:
        print('(get_by_iso) Warning: language by {} not found'.format(iso))
    else:
        return language[0]


def get_by_glot_id(glot_id):
    """
    get_by_glot_id('russ1263')
    >>> Russian
    """
    language = tuple(glottolog[glottolog.ID == glot_id].Name)
    if not language:
        print('(get_by_glot_id) Warning: language by {} not found'.format(glot_id))
    else:
        return language[0]

#---------------------------------------------------------------------------------


def get_glot_id_by_iso(iso):
    """
    get_glot_id_by_iso('rus')
    >>> russ1263
    """
    glot_id = tuple(glottolog[glottolog.ISO639P3code == iso].ID)
    if not glot_id:
        print('(get_glot_id_by_iso) Warning: glot_id by {} not found'.format(iso))
    else:
        return glot_id[0]


def get_iso_by_glot_id(glot_id): 
    """
    get_iso_by_glot_id('russ1263')
    >>> rus
    """
    iso = tuple(glottolog[glottolog.ID == glot_id].ISO639P3code)
    if not iso:
        print('(get_iso_by_glot_id) Warning: ISO by {} not found'.format(iso))
    else:
        return iso[0]
