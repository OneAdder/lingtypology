import folium
import pandas
import branca.colormap


legend_html = '''
              <div style="position: fixed; 
                          bottom: 50px;
                          left: 50px;
                          width: 250px;
                          height: 300px; 
                          border:2px solid grey;
                          z-index:9999;
                          font-size:14px;
                          ">
              '''

csv = pandas.read_csv('glottolog.csv', delimiter='\t', header=0)

def get_affiliations(languages):
    affiliations = []
    for language in languages:
        affiliations.append(tuple(csv[csv.language == language].affiliation)[0])
    return affiliations


class LingMapError(Exception):
    def __init__(self,value):
        self.msg = value
    def __str__(self):
        return self.msg


class LingMap(object):
    colors = ['#0000FF', '#8A2BE2', '#A52A2A', '#DEB887', '#5F9EA0', '#7FFF00', '#D2691E', '#FF7F50', '#6495ED', '#F08080', '#000000', '#ffffff']
    
    def __init__(self, languages):
        self.languages = languages

    def _get_coordinates(self, language):
        longitude = float(csv[csv.language == language].longitude)
        latitude = float(csv[csv.language == language].latitude)
        return (latitude, longitude)

    def _get_glot_id(self,language):
        return tuple(csv[csv.language == language].glottocode)[0]

    def add_features(self, features, numeric=False):
        self._sanity_check(features, feature_name='features')
        self.features = features
        if numeric:
            self.numeric = True
        else:
            self.numeric = False

    def add_popups(self, popups):
        self._sanity_check(popups, feature_name='popups')
        self.popups = popups

    def add_tooltips(self, tooltips):
        self._sanity_check(features, feature_name='tooltips')
        self.tooltips = tooltips

    def add_custom_coordinates(self, custom_coordinates):
        self._sanity_check(custom_coordinates, feature_name='custom_coordinates')
        self.custom_coordinates = custom_coordinates

    def add_custom_colors(self, colors):
        if 'features' in dir(self):
            if len(set(features)) == len(colors):
                self.colors = colors
            else:
                self.colors = colors + self.colors
        else:
            raise LingMapError('Colors cannot be set without features')

    def _sanity_check(self, features, feature_name='corresponding lists'):
        if len(self.languages) != len(features):
            raise LingMapError("Length of languages and {} does not match".format(feature_name))
    
    def _create_map(self):
        m = folium.Map(location=[0, 0], zoom_start=3)
        if 'features' in dir(self):
            if self.numeric:
                features = self.features
                features.sort()
                colormap = branca.colormap.LinearColormap(colors=['#e6ccff','#4a008f'], index=[features[0],features[-1]], vmin=features[0], vmax=features[-1])
                colors = [colormap(feature) for feature in features]
            else:
                mapping = {}
                legend = legend_html
                clear_features = []
                for i in self.features:
                    if i not in clear_features:
                        clear_features.append(i)
                for i, feature in enumerate(clear_features):
                    mapping[feature] = self.colors[i]
                    legend += '<a style="color: {};font-size: 150%;margin-left:20px;">●</a> — {}<br>'.format(self.colors[i], feature)
                colors = [mapping[f] for f in self.features]
        
        for i, language in enumerate(self.languages):
            if 'custom_coordinates' in dir(self):
                coordinates = self.custom_coordinates[i]
            else:
                coordinates = self._get_coordinates(language)
            if 'features' in dir(self):
                color = colors[i]
            else:
                color = '#DEB887'
            marker = folium.CircleMarker(
                        location=[coordinates[0], coordinates[1]],
                        radius=7,
                        fill=True,
                        weight=1,
                        fill_opacity=1,
                        color='#000000',
                        fill_color=color
                    )
            popup_href = '''<a href="https://glottolog.org/resource/languoid/id/{}" onclick="this.target='_blank';">{}</a><br>'''
            if 'popups' in dir(self):
                popup = folium.Popup(popup_href.format(self._get_glot_id(language), language) + self.popups[i])
            else:
                popup = folium.Popup(popup_href.format(self._get_glot_id(language), language))
            popup.add_to(marker)
            if 'tooltips' in dir(self):
                tooltip = folium.Tooltip(self.tooltips[i])
                tooltip.add_to(marker)
            marker.add_to(m)
        if 'features' in dir(self):
            if self.numeric:
                m.add_child(colormap)
            else:
                legend += '</div>'
                m.get_root().html.add_child(folium.Element(legend))

        return m

    def save(self, path):
        self._create_map().save(path)

    def render(self):
        return self._create_map().get_root().render()

def random_test():
    languages = ["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"]
    m = LingMap(languages)

    affs = get_affiliations(languages)
    features = ["Agglutinative", "Agglutinative", "Inflected", "Inflected", "Analythic"]

    m.add_features(features)
    m.add_popups(affs)
    m.add_tooltips(languages)
    m.add_custom_colors(("yellowgreen", "navy", "black"))
    m.save('test_map.html')

def circassian_test():
    circassian = pandas.read_csv('circassian.csv', delimiter=',', header=0)

    coordinates = list(zip(list(circassian.latitude), list(circassian.longitude)))
    features = list(circassian.dialect)

    languages = list(circassian.language)
    popups = list(circassian.village)

    m = LingMap(languages)
    m.add_features(features)
    m.add_popups(popups)
    m.add_tooltips(languages)
    m.add_custom_coordinates(coordinates)
    m.save('test_map.html')

def ejectives_test():
    data = pandas.read_csv('ejective_and_n_consonants.csv', delimiter=',', header=0)
    languages = list(data.language)
    consonants = list(data.consonants)
    ejectives = list(data.consonants)
    m = LingMap(languages)
    m.add_features(consonants, numeric=True)
    m.save('test_map.html')

ejectives_test()
