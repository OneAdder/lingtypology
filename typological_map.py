import folium
import folium.plugins

import branca.colormap
import branca.element

import jinja2
import pandas

legend_html = ''
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
    colors = ['#0000FF', '#8A2BE2', '#A52A2A', '#DEB887', '#5F9EA0', '#7FFF00', '#D2691E',
              '#FF7F50', '#6495ED', '#F08080', '#00FFFF', '#40E0D0', '#778899', '#FF6347',
              '#4682B4', '#6495ED', '#FFE4C4', '#BC8F8F', '#800000', '#000000', '#ffffff']
    shapes = ['⬤', '◼', '▲', '◯', '◻', '△', '◉', '▣', '◐', '◧', '◭', '◍','▤', '▶']
    start_location = (0, 0)
    start_zoom = 3
    minimap = {}
    colormap_colors = ('#e6ccff','#4a008f')
    languages_in_popups = True
    use_shapes = False
    control_scale = True
    control = False
    stroke_control = False
    control_position = 'topright'
    legend = True
    stroke_legend = True
    legend_title = 'Legend'
    stroke_legend_title = 'Legend'
    legend_position = 'bottomright'
    stroke_legend_position = 'bottomleft'
    rectangles = []
    lines = []
    html_popups = False
    radius = 7
    stroke_radius = 12
    
    def __init__(self, languages):
        self.languages = languages

    def _get_coordinates(self, language):
        longitude = float(csv[csv.language == language].longitude)
        latitude = float(csv[csv.language == language].latitude)
        return (latitude, longitude)

    def _get_glot_id(self,language):
        return tuple(csv[csv.language == language].glottocode)[0]

    def _create_popups(self, marker, language, i, parse_html=False):
        popup_href = '''<a href="https://glottolog.org/resource/languoid/id/{}" onclick="this.target='_blank';">{}</a><br>'''
        if self.languages_in_popups:
            if 'popups' in dir(self):
                if parse_html:
                    raise LingMapError('''
                                       It is impossible to add both language links and large HTML strings.
                                       You can either not use parse_html option or set ling_map_object.languages_in_popups = False.
                                       ''')
                popup = folium.Popup(popup_href.format(self._get_glot_id(language), language) + self.popups[i])
            else:
                popup = folium.Popup(popup_href.format(self._get_glot_id(language), language))
            popup.add_to(marker)
        else:
            if 'popups' in dir(self):
                if parse_html:
                    iframe = folium.IFrame(html=self.popups[i])
                    popup = folium.Popup(iframe)
                else:
                    popup = folium.Popup(self.popups[i])
                popup.add_to(marker)

    def _create_legend(self, m, legend_data, title='Legend', position='bottomright'):
        with open('legend.html', 'r', encoding='utf-8') as f:
            template = f.read()
        template = jinja2.Template(template)
        template = template.render(data=legend_data, position=position, title=title, use_shapes=self.use_shapes)
        template = '{% macro html(this, kwargs) %}' + template + '{% endmacro %}'
        macro = branca.element.MacroElement()
        macro._template = branca.element.Template(template)
        m.get_root().add_child(macro)

    def _set_marker(self,
                    location,
                    radius=7,
                    fill=True,
                    stroke=False,
                    weight=1,
                    fill_opacity=1,
                    color='#000000',
                    fill_color='#DEB887',
                    shape=''):
        if shape:
            div = folium.DivIcon(html=('<div style="font-size: 170%">' + str(shape) + '</div>'))
            marker = folium.Marker(location=location, icon=div)
        else:
            marker = folium.CircleMarker(
                location=location,
                radius=radius,
                fill=fill,
                stroke=stroke,
                weight=weight,
                fill_opacity=fill_opacity,
                color=color,
                fill_color=fill_color)
        return marker

    def _prepare_features(self, features, stroke=False, use_shapes=False):
        colors = self.colors
        if use_shapes:
            colors = self.shapes
        if stroke:
            colors.reverse()
        if self.numeric and not stroke:
            features.sort()
            colormap = branca.colormap.LinearColormap(colors=self.colormap_colors, index=[features[0],features[-1]], vmin=features[0], vmax=features[-1])
            groups_features = [(0, colormap(feature)) for feature in features]
            data = colormap
        else:
            mapping = {}
            clear_features = []
            groups = []
            data = ''
            for i, feature in enumerate(features):
                if feature not in clear_features:
                    clear_features.append(feature)
                    groups.append(folium.FeatureGroup(name=features[i]))
            for i, feature in enumerate(clear_features):
                mapping[feature] = (groups[i], colors[i])
                if use_shapes:
                    data += '<li><span style="color: #000000; text-align: center; opacity:0.7;">{}</span>{}</li>\n'.format(colors[i], feature)
                else:
                    data += '<li><span style="background: {};opacity:0.7;"></span>{}</li>\n'.format(colors[i], feature)
            groups_features = [mapping[f] for f in features]
        return (groups_features, data)

    def add_features(self, features, radius=7, numeric=False, control=False, use_shapes=False):
        self._sanity_check(features, feature_name='features')
        self.features = features
        self.radius = 7
        if numeric:
            self.numeric = True
        else:
            self.numeric = False
        if control:
            self.control = True
        if use_shapes:
            self.use_shapes = True

    def add_stroke_features(self, features, radius=12, numeric=False, control=False):
        self._sanity_check(features, feature_name='stroke features')
        self.stroke_features = features
        if numeric:
            self.s_numeric = True
        else:
            self.s_numeric = False
        if control:
            self.stroke_control = True
        self.stroke_radius = 12

    def add_popups(self, popups, parse_html=False):
        self._sanity_check(popups, feature_name='popups')
        self.popups = popups
        if parse_html:
            self.html_popups=True

    def add_tooltips(self, tooltips):
        self._sanity_check(tooltips, feature_name='tooltips')
        self.tooltips = tooltips

    def add_custom_coordinates(self, custom_coordinates):
        self._sanity_check(custom_coordinates, feature_name='custom_coordinates')
        self.custom_coordinates = custom_coordinates

    def add_minimap(self, position='bottomleft', width=150, height=150, collapsed_width=25, collapsed_height=25, zoom_animation=True):
        self.minimap = {'position': position, 'width': width, 'height': height, 'collapsed_width': collapsed_width, 'collapsed_height': collapsed_height, 'zoom_animation': zoom_animation}

    def add_minichart(self, data):
        self._sanity_check(data, feature_name='minicharts')
        self.minicharts = data

    def add_rectangle(self, locations, tooltip='', popup='', color='black'):
        self.rectangles.append({'bounds': locations, 'tooltip': tooltip, 'popup': popup, 'color': color})

    def add_line(self, locations, tooltip='', popup='', color='black', smooth_factor=1.0):
        self.lines.append({'locations': locations, 'tooltip': tooltip, 'popup': popup, 'color': color, 'smooth_factor': smooth_factor})

    def _sanity_check(self, features, feature_name='corresponding lists'):
        if len(self.languages) != len(features):
            raise LingMapError("Length of languages and {} does not match".format(feature_name))
    
    def _create_map(self):
        m = folium.Map(location=self.start_location, zoom_start=self.start_zoom, control_scale=self.control_scale)
        default_group = folium.FeatureGroup()
        markers = []
        stroke_markers = []
        s_markers = []
        s_stroke_markers = []
        s_marker = ''
        s_stroke_marker = ''
        if 'features' in dir(self):
            prepared = self._prepare_features(self.features, use_shapes=self.use_shapes)
            groups_features = prepared[0]
            data = prepared[1]

        if 'stroke_features' in dir(self):
            prepared = self._prepare_features(self.stroke_features, stroke=True, use_shapes=self.use_shapes)
            s_groups_features = prepared[0]
            s_data = prepared[1]
        
        for i, language in enumerate(self.languages):
            stroke_marker = False
            radius = self.radius
            stroke_radius = radius * 1.15
            if 'custom_coordinates' in dir(self):
                coordinates = self.custom_coordinates[i]
            else:
                coordinates = self._get_coordinates(language)
                
            if 'features' in dir(self):
                color_shape = groups_features[i][1]
            else:
                color_shape = '#DEB887'
                
            if 'stroke_features' in dir(self):
                marker = self._set_marker([coordinates[0], coordinates[1]], fill_color=color_shape)
                stroke_marker = self._set_marker([coordinates[0], coordinates[1]], stroke=True, radius=radius*1.15, fill_color='#000000')
                s_marker = self._set_marker([coordinates[0], coordinates[1]], radius=self.stroke_radius, fill_color=s_groups_features[i][1])
                s_stroke_marker = self._set_marker([coordinates[0], coordinates[1]], stroke=True, radius=self.stroke_radius*1.15, fill_color='#000000')
            else:
                if self.use_shapes:
                    marker = self._set_marker([coordinates[0], coordinates[1]], fill_color='#000000', shape=color_shape)
                else:
                    marker = self._set_marker([coordinates[0], coordinates[1]], radius=radius, fill_color=color_shape)
                    stroke_marker = self._set_marker([coordinates[0], coordinates[1]], stroke=True, radius=stroke_radius, fill_color='#000000')
            
            self._create_popups(marker, language, i, parse_html=self.html_popups)

            if 'features' in dir(self) and not self.numeric and self.control:
                group = groups_features[i][0]
            elif 'stroke_features' in dir(self) and self.stroke_control:
                group = s_groups_features[i][0]
            else:
                group = default_group
                
            if 'tooltips' in dir(self):
                tooltip = folium.Tooltip(self.tooltips[i])
                tooltip.add_to(marker)

            markers.append((marker, group))
            if stroke_marker:
                stroke_markers.append((stroke_marker, group))
            if s_marker:
                s_markers.append((s_marker, group))
            if s_stroke_marker:
                s_stroke_markers.append((s_stroke_marker, group))

        if s_stroke_markers:
            [s_stroke_mark[0].add_to(s_stroke_mark[1]) for s_stroke_mark in s_stroke_markers]
        if s_markers:
            [s_mark[0].add_to(s_mark[1]) for s_mark in s_markers]
        if stroke_markers:
            [stroke_mark[0].add_to(stroke_mark[1]) for stroke_mark in stroke_markers]
        [mark[0].add_to(mark[1]) for mark in markers]
    
        if 'features' in dir(self):
            if self.numeric:
                m.add_child(default_group)
                colormap = data
                m.add_child(colormap)
            else:
                if self.control:
                    [m.add_child(fg[0]) for fg in groups_features]
                    folium.LayerControl(collapsed=False, position=self.control_position).add_to(m)
                elif self.stroke_control:
                    [m.add_child(fg[0]) for fg in s_groups_features]
                    folium.LayerControl(collapsed=False, position=self.control_position).add_to(m)
                else:
                    m.add_child(default_group)
                
                if self.legend:
                    self._create_legend(m, data, title=self.legend_title, position=self.legend_position)
                if 'stroke_features' in dir(self) and self.stroke_legend:
                    self._create_legend(m, s_data, title=self.stroke_legend_title, position=self.stroke_legend_position)
        else:
            m.add_child(default_group)
        if self.minimap:
            minimap = folium.plugins.MiniMap(**self.minimap)
            m.add_child(minimap)
        if self.rectangles:
            for rectangle in self.rectangles:
                folium.Rectangle(**rectangle).add_to(m)
        if self.lines:
            for line in self.lines:
                folium.PolyLine(**line).add_to(m)
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

    m.add_features(features, control=True, use_shapes=True)
    m.add_popups(affs)
    m.add_tooltips(languages)
    #m.colors = ("yellowgreen", "navy", "blue")
    m.add_minimap()
    m.save('random.html')

def circassian_test():
    circassian = pandas.read_csv('circassian.csv', delimiter=',', header=0)

    coordinates = list(zip(list(circassian.latitude), list(circassian.longitude)))
    dialects = list(circassian.dialect)

    languages = list(circassian.language)
    popups = list(circassian.village)

    m = LingMap(languages)
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
    m.stroke_legend_position = 'right'
    #m.legend_position = 'topleft'
    m.stroke_legend_title = 'Languages'
    m.legend_title = 'Dialects'
    m.save('circassian.html')

def ejectives_test():
    data = pandas.read_csv('ejective_and_n_consonants.csv', delimiter=',', header=0)
    languages = list(data.language)
    consonants = list(data.consonants)
    ejectives = list(data.consonants)
    
    m = LingMap(languages)
    m.add_features(consonants, numeric=True)
    #m.languages_in_popups = False
    m.save('ejectives.html')


def circassian2_test():
    circassian = pandas.read_csv('circassian.csv', delimiter=',', header=0)

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
    m.save('simplest_test.html')

simplest_test()
random_test()
circassian_test()
ejectives_test()
circassian2_test()


