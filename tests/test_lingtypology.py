import os

import pandas
from lingtypology import *

import pytest


@pytest.fixture
def circassian():
    return pandas.read_csv(
        os.path.join(os.path.dirname(__file__), 'data', 'circassian.csv'),
        delimiter=',',
        header=0)



@pytest.fixture
def ejective_and_n_consonants():
    return pandas.read_csv(
        os.path.join(os.path.dirname(__file__), 'data', 'ejective_and_n_consonants.csv'),
        delimiter=',',
        header=0)

def test_LingMap(tmpdir):
    """The most basic test for LingMap"""
    m = LingMap(('Romanian', 'Ukrainian'))
    m.title = 'Simplest Test'
    m.save(str(tmpdir.join('simplest_test.html')))

def test_LingMap_features1(circassian):
    """LingMap with features (normal + stroke)"""
    coordinates = zip(list(circassian.latitude), list(circassian.longitude))
    dialects = circassian.dialect

    languages = circassian.language
    popups = circassian.village

    m = LingMap(languages)
    m.start_location = 'Caucasus'
    m.add_features(dialects)
    m.add_stroke_features(languages)
    m.add_popups(popups)
    m.add_tooltips(languages)
    m.add_custom_coordinates(coordinates)
    m.add_rectangle(((44.443206, 42.735694), (42.927524, 44.577277)), tooltip='Square Enix', popup='FFX', color='green')
    m.add_line(((44.5, 39), (43, 43)))
    m.stroke_legend_position = 'topright'
    m.stroke_legend_title = 'Languages'
    m.legend_title = 'Dialects'
    m.title = 'Circassian Dialects'
    m.render()
    
def test_LingMap_features2(ejective_and_n_consonants):
    """LingMap with features (colormap)"""
    data = ejective_and_n_consonants

    m = LingMap(data.language)
    m.legend_title = 'Amount of Consonants'
    m.stroke_legend_title = 'Amount of Vowels'
    m.colormap_colors = ('white', 'blue')
    m.add_tooltips(data.consonants)
    m.add_features(data.consonants, numeric=True)
    m.add_stroke_features(data.vowels, numeric = True)
    m.create_map()

def test_LingMap_features3():
    """LingMap with features (shapes + control)"""
    languages = ["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"]
    features = ["Agglutinative", "Agglutinative", "Inflected", "Inflected", "Analytic"]
    contents = ('Caucasus', 'Caucasus', 'Europe', 'Europe', 'Europe')
    
    m = LingMap(languages)
    html = \
        '''
        <a href="https://en.wikipedia.org/wiki/{data}" target="_blank">
        {data}
        </a>
        '''
    m.languages_in_popups = False
    m.add_popups([html.format(data=popup) for popup in contents], parse_html=True)
    m.add_features(features, use_shapes=True, control=True)
    m.create_map()

def test_LingMap_overlapping_features():
    languages = ('Tsakhur', 'Russian', 'Bulgarian')
    m = lingtypology.LingMap(languages)
    m.add_overlapping_features([
        ['ergative', 'has cases'],
        ['has cases', 'slavic'],
        ['slavic']
    ])
    m.create_map()

def test_LingMap_minicharts(ejective_and_n_consonants):
    data = ejective_and_n_consonants
    
    m = lingtypology.LingMap(data.language)
    m.add_minicharts(data.consonants, data.vowels)
    m.create_map()
    
def test_LingMap_empty():
    """It has to work, lol"""
    LingMap().create_map()

def test_Glottolog():
    languages = set()
    glottocodes = set()
    isos = set()
    coordinates = set()
    
    affiliations0_ex = 'Indo-European, Balto-Slavic, Slavic, East Slavic'
    macroarea_ex = 'Eurasia'
    
    languages.add(glottolog.get_by_iso('rus'))
    languages.add(glottolog.get_by_glot_id('russ1263'))
    
    glottocodes.add(glottolog.get_glot_id('Russian'))
    glottocodes.add(glottolog.get_glot_id_by_iso('rus'))
    
    isos.add(glottolog.get_iso('Russian'))
    isos.add(glottolog.get_iso_by_glot_id('russ1263'))
    
    coordinates.add(glottolog.get_coordinates('Russian'))
    coordinates.add(glottolog.get_coordinates_by_glot_id('russ1263'))
    coordinates = tuple(coordinates)
    
    affiliations0 = glottolog.get_affiliations(('Russian', 'English'))[0]
    macroarea = glottolog.get_macro_area('Russian')
    
    assertion = \
        languages == {'Russian'} and \
        glottocodes == {'russ1263'} and \
        isos == {'rus'} and \
        len(coordinates) == 1 \
            and isinstance(coordinates[0], tuple) \
            and len(coordinates[0]) == 2 and \
        affiliations0 == affiliations0_ex and \
        macroarea == macroarea_ex
    assert assertion
    
def test_wals():
    db_apis.Wals('1a', '20a', '3a').get_df(join_how='outer')

def test_autotyp():
    db_apis.Autotyp('Gender', 'Agreement').get_df()

def test_afbo():
    db_apis.AfBo('adverbializer', 'case: non-locative peripheral case').get_df()

def test_sails():
    db_apis.Sails('ICU10', 'ICU11').get_df()

def test_phoible():
    db_apis.Phoible().get_df(strip_na=['tones'])
    db_apis.Phoible(aggregated=False).get_df()
