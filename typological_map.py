import folium
import pandas

colors = ['#0000FF', '#8A2BE2', '#A52A2A', '#DEB887', '#5F9EA0', '#7FFF00', '#D2691E', '#FF7F50', '#6495ED']

legend_html = '''
              <div style="position: fixed; 
                          bottom: 50px;
                          left: 50px;
                          width: 250px;
                          height: 170px; 
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

class LingMap(object):
    def __init__(self, languages):
        self.languages = languages

    def _get_coordinates(self, language):
        longitude = float(csv[csv.language == language].longitude)
        latitude = float(csv[csv.language == language].latitude)
        return (longitude, latitude)

    def _get_glot_id(self,language):
        return tuple(csv[csv.language == language].glottocode)[0]

    def add_features(self, features):
        self.features = features

    def add_popups(self, popups):
        self.popups = popups
    
    def _create_map(self):
        m = folium.Map(location=[0, 0], zoom_start=2)
        if 'features' in dir(self):
            features = []
            mapping = {}
            legend = legend_html
            clear_features = set(self.features)
            for i, feature in enumerate(clear_features):
                mapping[feature] = colors[i]
                legend += '<a style="color: {};font-size: 150%;margin-left:20px;">●</a> — {}<br>'.format(colors[i], feature)
            features = [mapping[f] for f in self.features]

        for i, language in enumerate(self.languages):
            coordinates = self._get_coordinates(language)
            if 'features' in dir(self):
                color = features[i]
            else:
                color = '#DEB887'
            if 'popups' in dir(self):
                popup_href = '''<a href="https://glottolog.org/resource/languoid/id/{}" onclick="this.target='_blank';">{}</a><br>'''
                popup = popup_href.format(self._get_glot_id(language), language) + self.popups[i]
                folium.CircleMarker(
                        location=[coordinates[1], coordinates[0]],
                        radius=5,
                        fill=True,
                        fill_opacity=1,
                        color=color,
                        popup=popup
                    ).add_to(m)
            else:
                folium.CircleMarker(
                            location=[coordinates[1], coordinates[0]],
                            radius=5,
                            fill=True,
                            fill_opacity=1,
                            color=color
                        ).add_to(m)
        if 'features' in dir(self):
            legend += '</div>'
            m.get_root().html.add_child(folium.Element(legend))
        return m

    def save(self, path):
        self._create_map().save(path)

    def render(self):
        return self._create_map().get_root().render()
    

m = LingMap(["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"])

affs = get_affiliations(["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"])
features = ["Agglutinative", "Agglutinative", "Inflected", "Inflected", "Analythic"]

m.add_features(features)
m.add_popups(affs)
m.save('test_map.html')

