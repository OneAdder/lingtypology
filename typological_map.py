import folium
import pandas

colors = ['#0000FF', '#8A2BE2', '#A52A2A', '#DEB887', '#5F9EA0', '#7FFF00', '#D2691E', '#FF7F50', '#6495ED']

class MapFeature(object):
    def __init__(self, languages):
        self.languages = languages

    def _get_coordinates(self, language):
        longitude = float(csv[csv.language == language].longitude)
        latitude = float(csv[csv.language == language].latitude)
        return (longitude, latitude)

    def add_features(self, features):
        self.features = features
    
    def render(self):
        m = folium.Map()
        if self.features:
            features = []
            mapping = {}
            clear_features = set(self.features)
            for i, feature in enumerate(clear_features):
                mapping[feature] = colors[i]
            features = [mapping[f] for f in self.features]
        else:
            
        for language in self.languages:
            coordinates = self._get_coordinates(language)
            folium.CircleMarker(
                        location=[coordinates[1], coordinates[0]],
                        radius=5,
                        fill=True,
                        fill_opacity=1
                    ).add_to(m)
        m.save('test')
    
csv = pandas.read_csv('glottolog.csv', delimiter='\t', header=0)
#print(csv[csv.language == 'German'].longitude)
#print(csv[csv.language == 'Teojomulco Chatino'].longitude)

m = MapFeature(["Adyghe", "Kabardian", "Polish", "Russian", "Bulgarian"])
m.add_features(['NC', 'NC', 'Slavic', 'Slavic', 'Slavic'])
m.render()
