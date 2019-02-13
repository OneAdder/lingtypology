import pandas

glottolog_original = pandas.read_csv('glottolog.csv', delimiter='\t', header=0)

'''
get_affiliations(('Russian', 'English'))
>>> ['Indo-European, Slavic, East', 'Indo-European, Germanic, West, English']
'''
def get_affiliations(languages):
    affiliations = []
    for language in languages:
        affiliation = tuple(glottolog_original[glottolog_original.language == language].affiliation)
        if not affiliation:
            print('(get_affiliations) Warning: affiliation for {} not found'.format(language))
            affiliations.append('')
        else:
            affiliations.append(affiliation[0])
    return affiliations

'''
get_coordinates('Russian')
>>> (59.0, 50.0)
'''
def get_coordinates(language):
    latitude = glottolog_original[glottolog_original.language == language].latitude
    longitude = glottolog_original[glottolog_original.language == language].longitude
    if not list(latitude) or not list(longitude):
        print('(get_coordinates) Warning: coordinates for {} not found'.format(language))
    else:
        return (float(latitude), float(longitude))

'''
get_glot_id(language)
>>> russ1263
'''
def get_glot_id(language):
    glot_id = tuple(glottolog_original[glottolog_original.language == language].glottocode)
    if not glot_id:
        print('(get_glot_id) Warning: Glottolog ID for {} not found'.format(language))
    else:
        return glot_id[0]

'''
get_macro_area('Russian')
>>> Eurasia
'''
def get_macro_area(language):
    macro_area = tuple(glottolog_original[glottolog_original.language == language].area)
    if not macro_area:
        print('(get_macro_area) Warning: Macro area for {} not found'.format(language))
    else:
        return macro_area[0]

'''
get_country('Russian')
>>> Canada, Czech Republic, Lithuania, Mongolia, ...
'''
def get_country(language):
    country = tuple(glottolog_original[glottolog_original.language == language].country)
    if not country:
        print('(get_country) Warning: country for {} not found'.format(language))
    else:
        return country[0]

'''
get_iso('Russian')
>>> rus
'''
def get_iso(language):
    iso = tuple(glottolog_original[glottolog_original.language == language].iso)
    if not iso:
        print('(get_iso) Warning: ISO for {} not found'.format(language))
    else:
        return iso[0]

#---------------------------------------------------------------------------------

'''
get_by_affiliation('Indo-European, Slavic, East')
>>> ('Ukrainian', 'Rusyn', 'Russian', 'Belarusian')
'''
def get_by_affiliation(affiliation):
    languages = tuple(glottolog_original[glottolog_original.affiliation == affiliation].language)
    if not languages:
        print('(get_by_affiliation) Warning: languages by {} not found'.format(affiliation))
    else:
        return languages

'''
get_by_iso('rus')
>>> Russian
'''
def get_by_iso(iso):
    language = tuple(glottolog_original[glottolog_original.iso == iso].language)
    if not language:
        print('(get_by_iso) Warning: language by {} not found'.format(iso))
    else:
        return language[0]

'''
get_by_glot_id('russ1263')
>>> Russian
'''
def get_by_glot_id(glot_id):
    language = tuple(glottolog_original[glottolog_original.glottocode == glot_id].language)
    if not language:
        print('(get_by_glot_id) Warning: language by {} not found'.format(glot_id))
    else:
        return language[0]

#---------------------------------------------------------------------------------

'''
get_glot_id_by_iso('rus')
>>> russ1263
'''
def get_glot_id_by_iso(iso):
    glot_id = tuple(glottolog_original[glottolog_original.iso == iso].glottocode)
    if not glot_id:
        print('(get_glot_id_by_iso) Warning: glot_id by {} not found'.format(iso))
    else:
        return glot_id[0]

'''
get_iso_by_glot_id('russ1263')
>>> rus
'''
def get_iso_by_glot_id(glot_id):
    iso = tuple(glottolog_original[glottolog_original.glottocode == glot_id].iso)
    if not iso:
        print('(get_iso_by_glot_id) Warning: ISO by {} not found'.format(iso))
    else:
        return iso[0]

