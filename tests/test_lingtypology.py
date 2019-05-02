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


def test_random(tmpdir):
    languages = ["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"]
    m = LingMap(languages)

    affs = glottolog.get_affiliations(languages)
    features = ["Agglutinative", "Agglutinative", "Inflected", "Inflected", "Analythic"]

    m.add_features(features, control=True, use_shapes=True)
    m.add_popups(affs)
    m.add_tooltips(languages)
    #m.colors = ("yellowgreen", "navy", "blue")
    m.add_minimap()
    m.save(str(tmpdir.join('random.html')))

def test_circassian(tmpdir, circassian):
    coordinates = zip(list(circassian.latitude), list(circassian.longitude))
    dialects = circassian.dialect

    languages = circassian.language#list(circassian.language)
    popups = circassian.village

    m = LingMap(languages)
    #m.unstroked = False
    m.start_location = (44.21, 42.32)
    m.start_zoom = 8
    m.add_features(dialects)#, control=True)
    #m.control_position = 'bottomleft'
    m.add_stroke_features(languages)
    m.add_popups(popups)
    m.add_tooltips(languages)
    m.add_custom_coordinates(coordinates)
    #m.add_rectangle(((44.443206, 42.735694), (42.927524, 44.577277)), tooltip='Square Enix', popup='FFX', color='green')
    #m.add_line(((44.5, 39), (43, 43)))
    #m.legend = False
    #m.stroke_legend = False
    m.stroke_legend_position = 'topright'
    #m.legend_position = 'topleft'
    m.stroke_legend_title = 'Languages'
    m.legend_title = 'Dialects'
    #m.title = 'Circassian Dialects'
    m.save(str(tmpdir.join('circassian.html')))

def test_ejectives(tmpdir, ejective_and_n_consonants):
    data = ejective_and_n_consonants

    m = LingMap(data.language)
    m.legend_title='Amount of consonants'
    m.add_tooltips(data.consonants)
    m.add_features(data.consonants, numeric=True)
    #m.languages_in_popups = False
    m.save(str(tmpdir.join('ejectives.html')))


def test_circassian2(tmpdir, circassian):
    coordinates = zip(list(circassian.latitude), list(circassian.longitude))
    dialects = circassian.dialect

    languages = circassian.language
    popups = circassian.village

    m = LingMap(languages)
    #m.shapes = range(1, 20)
    m.start_location = (44.21, 42.32)
    m.start_zoom = 8
    m.add_custom_coordinates(coordinates)
    m.add_features(dialects, use_shapes=True)
    m.save(str(tmpdir.join('circassian2_test.html')))

def test_simplest(tmpdir):
    m = LingMap(('Romanian', 'Ukrainian'))
    m.title = 'Simplest Test'
    m.save(str(tmpdir.join('simplest_test.html')))

def test_heatmap_only(tmpdir, circassian):
    coordinates = list(zip(list(circassian[circassian.language == 'Kabardian'].latitude), list(circassian[circassian.language == 'Kabardian'].longitude)))
    m = LingMap([])
    m.start_zoom = 6
    m.start_location = (44.21, 42.32)
    m.add_heatmap(coordinates)
    m.save(str(tmpdir.join('heatmap_only.html')))

def test_heatmap(tmpdir, circassian):
    coordinates = zip(list(circassian.latitude), list(circassian.longitude))
    dialects = circassian.dialect

    languages = circassian.language
    popups = circassian.village

    m = LingMap(languages)
    m.start_location = (44.21, 42.32)
    m.start_zoom = 6
    m.add_custom_coordinates(coordinates)
    m.legend_title = 'Languages'
    m.add_heatmap(coordinates)
    m.save(str(tmpdir.join('heatmap.html')))
    
def test_wals(tmpdir):
    wals_page = Wals(('1a',)).get_df()
    
    m = LingMap(wals_page.language)
    m.add_custom_coordinates(wals_page.coordinates)
    m.add_features(wals_page._1A)
    m.legend_title = 'Consonant Inventory'
    m.save(str(tmpdir.join('wals_test.html')))

def test_wals_heatmap(tmpdir):
    wals_page = Wals('1a').get_df()

    m = LingMap()
    m.add_heatmap(wals_page[wals_page._1A == 'Large'].coordinates)
    m.title = 'Large Consonant Inventories'
    m.save(str(tmpdir.join('wals_heatmap')))
