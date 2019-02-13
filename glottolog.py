import pandas

csv = pandas.read_csv('glottolog.csv', delimiter='\t', header=0)

'''
get_affiliations(('Russian', 'English'))
>>> ['Indo-European, Slavic, East', 'Indo-European, Germanic, West, English']
'''
def get_affiliations(languages):
    affiliations = []
    for language in languages:
        affiliation = tuple(csv[csv.language == language].affiliation)
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
    latitude = csv[csv.language == language].latitude
    longitude = csv[csv.language == language].longitude
    if not list(latitude) or not list(longitude):
        print('(get_coordinates) Warning: coordinates for {} not found'.format(language))
    else:
        return (float(latitude), float(longitude))

'''
get_glot_id(language)
>>> russ1263
'''
def get_glot_id(language):
    glot_id = tuple(csv[csv.language == language].glottocode)
    if not glot_id:
        print('(get_glot_id) Warning: Glottolog ID for {} not found'.format(language))
    else:
        return glot_id[0]


