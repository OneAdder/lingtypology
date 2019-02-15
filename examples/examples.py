import pandas
from lingtypology import *


def random_test():
    languages = ["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"]
    m = LingMap(languages)

    affs = glottolog.get_affiliations(languages)
    features = ["Agglutinative", "Agglutinative", "Inflected", "Inflected", "Analythic"]

    m.add_features(features, control=True, use_shapes=True)
    m.add_popups(affs)
    m.add_tooltips(languages)
    #m.colors = ("yellowgreen", "navy", "blue")
    m.add_minimap()
    m.save('random.html')

def circassian_test():
    circassian = pandas.read_csv('examples/circassian.csv', delimiter=',', header=0)

    coordinates = list(zip(list(circassian.latitude), list(circassian.longitude)))
    dialects = list(circassian.dialect)

    languages = list(circassian.language)
    popups = list(circassian.village)

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
    m.save('circassian.html')

def ejectives_test():
    data = pandas.read_csv('examples/ejective_and_n_consonants.csv', delimiter=',', header=0)
    languages = list(data.language)
    consonants = list(data.consonants)
    ejectives = list(data.consonants)
    
    m = LingMap(languages)
    m.add_features(consonants, numeric=True)
    #m.languages_in_popups = False
    m.save('ejectives.html')


def circassian2_test():
    circassian = pandas.read_csv('examples/circassian.csv', delimiter=',', header=0)

    coordinates = list(zip(list(circassian.latitude), list(circassian.longitude)))
    dialects = list(circassian.dialect)

    languages = list(circassian.language)
    popups = list(circassian.village)

    m = LingMap(languages)
    #m.shapes = range(1, 20)
    m.start_location = (44.21, 42.32)
    m.start_zoom = 8
    m.add_custom_coordinates(coordinates)
    m.add_features(dialects, use_shapes=True)
    m.save('circassian2_test.html')

def simplest_test():
    m = LingMap(('Romanian', 'Ukrainian'))
    m.unstroked = False
    m.save('simplest_test.html')

def heatmap_only_test():
    circassian = pandas.read_csv('examples/circassian.csv', delimiter=',', header=0)
    coordinates = list(zip(list(circassian[circassian.language == 'Kabardian'].latitude), list(circassian[circassian.language == 'Kabardian'].longitude)))
    m = LingMap([])
    m.start_zoom = 6
    m.start_location = (44.21, 42.32)
    m.add_heatmap(coordinates)
    m.save('heatmap_only.html')

def heatmap_test():
    circassian = pandas.read_csv('examples/circassian.csv', delimiter=',', header=0)

    coordinates = list(zip(list(circassian.latitude), list(circassian.longitude)))
    dialects = list(circassian.dialect)

    languages = list(circassian.language)
    popups = list(circassian.village)

    m = LingMap(languages)
    m.start_location = (44.21, 42.32)
    m.start_zoom = 6
    m.add_custom_coordinates(coordinates)
    m.legend_title = 'Languages'
    m.add_heatmap(coordinates)
    m.save('heatmap.html')
    
def wals_test():
    df = Wals(('1a',)).get_df()
    languages = list(df.language)
    features = list(df._1A)
    coordinates = list(zip(list(df.latitude), list(df.longitude)))
    
    m = LingMap(languages)
    m.add_custom_coordinates(coordinates)
    m.add_features(features)
    m.legend_title = 'Consonant Inventory'
    m.save('wals_test.html')

def wals_heatmap_test():
    df = Wals('1a').get_df()
    coordinates = list(zip(list(df[df._1A == 'Large'].latitude), list(df[df._1A == 'Large'].longitude)))

    m = LingMap()
    m.heatmap = coordinates
    m.save('wals_heatmap')

#simplest_test()
#random_test()
#circassian_test()
#ejectives_test()
#circassian2_test()
#heatmap_only_test()
#heatmap_test()
#wals_test()
#wals_heatmap_test()



