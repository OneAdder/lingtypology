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

def get_affiliations(languages):
    affiliations = []
    for language in languages:
        affiliations.append(str(csv[csv.language == language].affiliation))
    return affiliations

class LingMap(object):
    def __init__(self, languages):
        self.languages = languages

    def _get_coordinates(self, language):
        longitude = float(csv[csv.language == language].longitude)
        latitude = float(csv[csv.language == language].latitude)
        return (longitude, latitude)

    def add_features(self, features):
        self.features = features
    
    def render(self):
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
        m.save('test')
    
csv = pandas.read_csv('glottolog.csv', delimiter='\t', header=0)
#print(csv[csv.language == 'German'].longitude)
#print(csv[csv.language == 'Teojomulco Chatino'].longitude)
#print(get_affiliations(['Russian']))
m = LingMap(["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"])
features = get_affiliations(["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"])
m.add_features(features)
m.render()
