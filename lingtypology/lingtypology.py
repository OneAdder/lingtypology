"""This module draws a map"""

#Folium tools
import folium
import folium.plugins

#Branca tools
import branca.colormap
import branca.element

#Jinja2
import jinja2
#Pandas
import pandas
#Math
import math
#os
import os

#Local tools
import lingtypology.glottolog
from lingtypology.db_apis import Wals#, Phoible

class LingMapError(Exception):
    """All special exceptions"""
    def __init__(self,value):
        self.msg = value
    def __str__(self):
        return self.msg


class LingMap(object):
    """Lingtypology map object
    Parameter languages: list of strings, default []

    Attributes:
    -----------
    Features
    ---
    colors: list of html codes for colors
        Colors that represent features.
        You can either use the default colors or set yours.
    stroke_colors: list of html codes for colors
        Colors that represent additional (stroke) features.
        You can either use the default colors or set yours.
    shapes: list of characters
        If you use shapes instead of colors, you can either use the default shapes or set yours.
        Shapes are Unicode symbols.
    ---
    
    Map
    ---
    start_location: (float, float), default (0, 0)
        Coordinates of the map (latitude, longitude).
    start_zoom: int, default 2
        Imitial zoom level.
    control_scale: bool, default True
        Whether to add control scale.
    prefer_canvas: bool, default False
        Use canvas instead of SVG.
        If set to True, the map may be more responsive in case you have a lot of markers.
    title: str, default None
        You can add a title to the map.
    start_location_mapping: dict,
        Mapping between normal locations and coordinates.
    ---

    Legend
    ---
    legend: bool, default True
        Whether to add legend
    stroke_legend: bool True
        Whether to add stroke legend
    legend_title: str, default Legend
        Legend title
    stroke_legend_title: str, default Legend
        Stroke legend title
    legend_position: str, default 'bottomright'
        Legend position.
        Available values: 'right', 'left', 'top', 'bottom', 'bottomright', 'bottomleft', 'topright', 'topleft'
    stroke_legend_position: str, default 'bottomleft'
        Stroke legend position.
        Available values: 'right', 'left', 'top', 'bottom', 'bottomright', 'bottomleft', 'topright', 'topleft'
    ---

    Markers
    ---
    use_shapes: bool, default False
        Whether to use shapes instead of colors.
    radius: int, default 7
        Circle marker radius.
    stroke_radius: int, default 12
        Radius of markers if you use stroke features.
    stroked: bool, default True
        Whether to add stroke to markers.
    unstroked: bool, default True
        If set to True, circle marker will merge if you zoom out without stroke between them.
        It multiplies the number of markers by 2. For better performance set it to False.
        To understand how it looks see the example below.

        unstroked = True (default):
             ┌——————————┐
             │ ▒▒▒▒▒▒▒▒ │
             │ ▒▒▒▒▒▒▒▒ └—————┐
             │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │
             │ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │
             └—————┐ ▒▒▒▒▒▒▒▒ │
                   │ ▒▒▒▒▒▒▒▒ │
                   └——————————┘
        unstroked = False:
             ┌——————————┐
             │ ▒▒▒▒▒▒▒▒ │
             │ ▒▒▒▒▒┌———┴——————┐
             │ ▒▒▒▒▒│ ▒▒▒▒▒▒▒▒ │
             │ ▒▒▒▒▒│ ▒▒▒▒▒▒▒▒ │
             └——————┤ ▒▒▒▒▒▒▒▒ │
                    │ ▒▒▒▒▒▒▒▒ │
                    └——————————┘
                    
    ---

    Popups
    ---
    languages_in_popups: bool, default True
        Whether to show links to Glottolog website in popups
    html_popups: bool, default False
        Setting it to True allows to put full html pages into popups (using folium.IFrame).
    ---

    Control
    ---
    control: bool, default False
        Whether to add LayerControls and group by features.
    stroke_control: bool, default False
        Whether to add LayerControls and group by stroke features.
    control_position: str, default 'topright'
        Position of LayerControls.
        May be ‘topleft’, ‘topright’, ‘bottomleft’ or ‘bottomright’.
    ---

    Other
    ---
    heatmap_only: bool, default False
        If set to true no markers will be rendered.
    colormap_colors: tuple, default ('#ffffff','#4a008f')
        Default colors for the colormap.
    ---
    """
    
    def __init__(self, languages=[]):
        """__init__

        Sets self.languages turning it into a tuple.
        If no languages are given, sets self.heatmap_only to true.
        Then it sets everything else.
        """
        if isinstance(languages, str):
            languages = (languages,)
        if not isinstance(languages, tuple):
            languages = tuple(languages)
            
        if languages:
            self.languages = languages
            self.heatmap_only = False
        else:
            self.heatmap_only = True
        # Feature representation
        self.stroke_colors = ['#ffffff', '#000000', '#800000', '#BC8F8F', '#FFE4C4', '#6495ED', '#4682B4',
                         '#FF6347', '#778899', '#40E0D0', '#00FFFF', '#F08080', '#6495ED', '#FF7F50',
                         '#D2691E', '#7FFF00', '#5F9EA0', '#DEB887', '#A52A2A', '#8A2BE2', '#0000FF']
        self.colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6',
                  '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8','#800000',
                  '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']
        self.shapes = ['⬤', '◼', '▲', '◯', '◻', '△', '◉', '▣', '◐', '◧', '◭', '◍','▤', '▶']
        # Map
        self.start_location = (0, 0)
        self.start_zoom = 2
        self.control_scale = True
        self.prefer_canvas = False
        self.title = None
        # Legend
        self.legend = True
        self.stroke_legend = True
        self.legend_title = 'Legend'
        self.stroke_legend_title = 'Legend'
        self.legend_position = 'bottomright'
        self.stroke_legend_position = 'bottomleft'
        # Popups
        self.languages_in_popups = True
        self.html_popups = False
        # Markers
        self.use_shapes = False
        self.radius = 7
        self.stroke_radius = 12
        self.stroked = True
        self.unstroked = True
        # Control
        self.control = False
        self.stroke_control = False
        self.control_position = 'topright'
        # Colormap
        self.colormap_colors = ('#ffffff','#4a008f')
        # Heat map
        self.use_heatmap = False
        self.heatmap = []
        # Adding other stuff
        self.minimap = {}
        self.rectangles = []
        self.lines = []
        #Don't touch
        self._legend_id = 0
        self.features = None
        self.popups = None
        self.tooltips = None
        self.custom_coordinates = None
        self.stroke_features = None
        self.start_location_mapping = {
            'Central Europe': {'start_location': (50, 0), 'start_zoom': 4},
            'Caucasus': {'start_location': (43, 42), 'start_zoom': 6},
            'Australia & Oceania': {'start_location': (-16, 159), 'start_zoom': 3},
            'Papua New Guinea': {'start_location': (-5, 141), 'start_zoom': 6},
            'Africa': {'start_location': (3, 22), 'start_zoom': 3},
            'Asia': {'start_location': (36, 100), 'start_zoom': 3},
            'North America': {'start_location': (51, -102), 'start_zoom': 3},
            'Central America': {'start_location': (19, -81), 'start_zoom': 4},
            'South America': {'start_location': (-27, -49), 'start_zoom': 3},
        }

    def _create_popups(self, marker, language, i, parse_html=False):
        """Creates popups.

        Parameters
        ----------
        marker: folium.CircleMarker
            Marker to add the popup to.
        language: str
            Language name.
        i: int
            Number of the marker.
        parse_html: bool, default False
            Whether to use Folium.IFrame to add content to the popup
        """
        popup_href = '''<a href="https://glottolog.org/resource/languoid/id/{}" onclick="this.target='_blank';">{}</a><br>'''
        if self.languages_in_popups:
            if self.popups:
                if parse_html:
                    raise LingMapError('''
                                       It is impossible to add both language links and large HTML strings.
                                       You can either not use html_popups option or set ling_map_object.languages_in_popups = False.
                                       ''')
                popup = folium.Popup(popup_href.format(lingtypology.glottolog.get_glot_id(language), language) + self.popups[i])
            else:
                popup = folium.Popup(popup_href.format(lingtypology.glottolog.get_glot_id(language), language))
            popup.add_to(marker)
        else:
            if self.popups:
                if parse_html:
                    iframe = folium.IFrame(html=self.popups[i])
                    popup = folium.Popup(iframe)
                else:
                    popup = folium.Popup(self.popups[i])
                popup.add_to(marker)

    def _create_legend(self, m, legend_data, title='Legend', position='bottomright'):
        """Creates legend and adds it to the map

        m: folium.Map
            The map.
        legend_data: str
            Html string with the contents for the legend.
        title: str, default 'Legend'
            Legend title.
        position: str, default 'bottomright'
            Legend position.
        """
        module_directory = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(module_directory, 'legend.html'), 'r', encoding='utf-8') as f:
            template = f.read()
        template = jinja2.Template(template)
        template = template.render(data=legend_data, position=position, title=title, use_shapes=self.use_shapes, legend_id=self._legend_id)
        template = '{% macro html(this, kwargs) %}' + template + '{% endmacro %}'
        macro = branca.element.MacroElement()
        macro._template = branca.element.Template(template)
        m.get_root().add_child(macro)
        self._legend_id += 1

    def _create_heatmap(self, m, heatmap):
        """Creates heatmap and adds it to the map

        m: folium.Map
            The map.
        heatmap: list
            List of coordinates.
        """
        folium.plugins.HeatMap(heatmap).add_to(m)

    def _create_title(self, m, title):
        """Creates title and adds it to the map

        m: folium.Map
            The map.
        title: str
            Title.
        """
        template = '''
                    <div
                        style='position: absolute;
                        z-index:9999;
                        border:2px solid grey;
                        background-color:rgba(255, 255, 255, 0.8);
                        border-radius:6px;
                        padding: 10px;
                        font-size:20px;
                        top: 20px;
                        left: 50%;'
                    >
                    {{ title }}
                    </div>
                   '''
        template = jinja2.Template(template)
        template = template.render(title=title)
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
        """Sets marker

        Parameters
        ----------
        location: list
            List of coordinates.
        radius: int, default 7,
        fill: bool, default True,
        stroke: bool, default False,
        weight: int, default 1,
        fill_opacity: int, default 1,
        color: str, default '#000000',
        fill_color: str, default '#DEB887',
        shape: str, default ''

        Returns
        ----------
        marker: folium.CircleMarker
        """
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

    
    def _sort_all(self, features):
        """This crazy function is needed to sort everything by features for the colormap

        It takes all necessary attributes and sorts them by features.
        Parameters
        ----------
        features: str
            List of features

        Returns
        ----------
        features: str
        """
        attrs = [self.languages, self.popups, self.tooltips, self.custom_coordinates]
        length = [False for n in range(len(features))]
        attrs_r = []
        for attr in attrs:
            if attr:
                attrs_r.append(attr)
            else:
                attrs_r.append(length)
        al = list(zip(features, *attrs_r))
        al.sort(key=lambda element: element[0])
        features = []
        self.languages = []
        self.popups = []
        self.tooltips = []
        self.custom_coordinates = []
        for el in al:
            features.append(el[0])
            if el[1]:
                self.languages.append(el[1])
            if el[2]:
                self.popups.append(el[2])
            if el[3]:
                self.tooltips.append(el[3])
            if el[4]:
                self.custom_coordinates.append(el[4])
        self.features = features
        return features

    def _prepare_features(self, features, stroke=False, use_shapes=False):
        """Creates data for legend (depending on type of features) and creates features groups if needed

        Parameters
        ----------
        features: list of strings
            Features or stroke features.
        stroke: bool, default False
            Defines whether there are stroke features or not.
        use_shapes: bool, default False
            Whether to use shapes instead of colors.

        Returns
        ----------
        groups_features: tuple:
            folium.map.FeatureGroup or 0
                Feature group for the feature or 0 if it is not needed.
            str
                Color or shape.
        data: str
            HTML string of data for legend.
        """
        colors = self.colors
        if use_shapes:
            colors = self.shapes
        if stroke:
            colors = self.stroke_colors
        if self.numeric and not stroke:
            features = self._sort_all(features)
            colormap = branca.colormap.LinearColormap(colors=self.colormap_colors,
                                                      index=[features[0], features[-1]],
                                                      vmin=features[0],
                                                      vmax=features[-1],
                                                      caption=self.legend_title)
            groups_features = [(0, colormap(feature)) for feature in features]
            template =  '''
                        <style>
                            .grad {
                                height: 200px;
                                width: 20px;
                                background: linear-gradient({{ color0 }}, {{ color1 }});
                                }
                        </style>
                        <div class="grad"/>
                        <li style="margin-left: 35px;">{{ feature0 }}</li>
                        <li style="margin-left: 35px; margin-top: 170px;">{{ feature1 }}</li>
                        '''
            template = jinja2.Template(template)
            data = template.render(color0=self.colormap_colors[0],
                                   color1=self.colormap_colors[1],
                                   feature0=features[0],
                                   feature1=features[-1])
        else:
            mapping = {}
            clear_features = []
            groups = []
            data = []
            for i, feature in enumerate(features):
                if feature not in clear_features:
                    clear_features.append(feature)
                    groups.append(folium.FeatureGroup(name=features[i]))
            for i, feature in enumerate(clear_features):
                mapping[feature] = (groups[i], colors[i])
                data.append((str(feature), colors[i]))
            groups_features = [mapping[f] for f in features]
            data.sort()
            if use_shapes:
                html = '<li><span style="color: #000000; text-align: center; opacity:0.7;">{}</span>{}</li>'
            else:
                html = '<li><span style="background: {};opacity:0.7;"></span>{}</li>'
            data = '\n'.join([html.format(d[1], d[0]) for d in data])
        return (groups_features, data)

    def _create_unified_marker(self, coordinates, color_shape, s_color):
        """Creates several (<5, >0) markers that will look like one.

        Parameters
        ----------
        coordinates: tuple
            Tuple of (latitude, longitude).
        color_shape: str
            Color OR shape.
        s_color:
            Stroke color. It is not used if there are no stroke features.

        Returns
        ----------
        dict:
            'marker': folium.CircleMarker
                Base marker.

                ▒▒▒▒▒
                ▒▒▒▒▒
                ▒▒▒▒▒
                
            'stroke': folium.CircleMarker
                Marker that will look like stroke for the base marker.
                
               ┌———————┐
               │ ▒▒▒▒▒ │
               │ ▒▒▒▒▒ │
               │ ▒▒▒▒▒ │
               └———————┘
                
            's_marker': folium.CircleMarker
                Base marker for stroke features, it will look like big stroke.
                
              ▓▓▓▓▓▓▓▓▓▓▓▓▓
              ▓ ┌———————┐ ▓
              ▓ │ ▒▒▒▒▒ │ ▓
              ▓ │ ▒▒▒▒▒ │ ▓
              ▓ │ ▒▒▒▒▒ │ ▓
              ▓ └———————┘ ▓
              ▓▓▓▓▓▓▓▓▓▓▓▓▓
              
            's_stroke': folium.CircleMarker
                Marker that will look like stroke for s_marker.

             ┌———————————————┐
             │ ▓▓▓▓▓▓▓▓▓▓▓▓▓ │
             │ ▓ ┌———————┐ ▓ │
             │ ▓ │ ▒▒▒▒▒ │ ▓ │
             │ ▓ │ ▒▒▒▒▒ │ ▓ │
             │ ▓ │ ▒▒▒▒▒ │ ▓ │
             │ ▓ └———————┘ ▓ │
             │ ▓▓▓▓▓▓▓▓▓▓▓▓▓ │
             └———————————————┘  
        """
        marker = ''
        stroke = ''
        s_marker = ''
        s_stroke = ''
        if self.stroke_features:
            if self.unstroked:
                marker = self._set_marker([coordinates[0], coordinates[1]], fill_color=color_shape)
                stroke = self._set_marker([coordinates[0], coordinates[1]], stroke=True, radius=self.radius*1.15, fill_color='#000000')
                s_marker = self._set_marker([coordinates[0], coordinates[1]], radius=self.stroke_radius, fill_color=s_color)
                s_stroke = self._set_marker([coordinates[0], coordinates[1]], stroke=True, radius=self.radius*1.8, fill_color='#000000')
            else:
                marker = self._set_marker([coordinates[0], coordinates[1]], stroke=self.stroked, fill_color=color_shape)
                s_marker = self._set_marker([coordinates[0], coordinates[1]], stroke=self.stroked, radius=self.stroke_radius, fill_color=s_color)
        else:
            if self.use_shapes:
                marker = self._set_marker([coordinates[0], coordinates[1]], fill_color='#000000', shape=color_shape)
            else:
                if self.unstroked:
                    marker = self._set_marker([coordinates[0], coordinates[1]], radius=self.radius, fill_color=color_shape)
                    stroke = self._set_marker([coordinates[0], coordinates[1]], stroke=True, radius=self.radius*1.15, fill_color='#000000')
                else:
                    marker = self._set_marker([coordinates[0], coordinates[1]], stroke=self.stroked, radius=self.radius, fill_color=color_shape)
        return {'marker': marker, 'stroke': stroke, 's_marker': s_marker, 's_stroke': s_stroke}

    def add_features(self, features, radius=7, numeric=False, control=False, use_shapes=False):
        """Add features

        features: list of strings
            List of features. Length of the list should equal to length of languages.
            By default, if you add features, a legend will appear. To shut it down set
            "legend" attribute to False.
            To change the title of the legend use "legend_title" attribute.
        radius: int, default 7
            Marker radius.
        numeric: bool, default False
            Whether to assign different color to each feature (False),
            or to assign a color from colormap (True).
            You can set it to True only in case your features are numeric,
            for example "Number of phonemes", and stroke features are not given.
        control: bool, default False
            Whether to add LayerControls to the map.
            It allows interactive turning on/off given features.
        use_shapes: bool, default False
            Whether to use shapes instead of colors. This option allows to represent features as shapes.
            Shapes are Unicode charaters like ⬤ or ◼. You can replace or add to default symbols by
            changing attribute "shapes".
            If colors are not a viable option for you, you can set this option to True.
        """
        features = tuple(features)
        self._sanity_check(features, feature_name='features')
        self.features = features
        self.radius = radius
        if numeric:
            self.numeric = True
        else:
            self.numeric = False
        if control:
            self.control = True
        if use_shapes:
            self.use_shapes = True

    def add_stroke_features(self, features, radius=12, numeric=False, control=False):
        """Add stroke features

        This function assigns features to strokes of markers.
        
        features: list of strings
            List of features. Length of the list should equal to length of languages.
            By default, if you add features, a legend will appear. To shut it down set
            "stroke_legend" attribute to False.
            To change the title of the legend use "stroke_legend_title" attribute.
        radius: int, default 12
            Marker radius.
        control: bool, default False
            Whether to add LayerControls to the map.
            It allows interactive turning on/off given features.
        """
        features = tuple(features)
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
        """Add popups to markers

        popups: list of strings
            List of popups. Length of the list should equal to length of languages.
        parse_html: bool, default False
            By default (False) you can add small pieces of html code.
            If you need to add full html pages to popups, you need to set the option to True.
        """
        popups = tuple(popups)
        self._sanity_check(popups, feature_name='popups')
        self.popups = popups
        if parse_html:
            self.html_popups=True

    def add_tooltips(self, tooltips):
        """Add tooltips to markers

        tooltips: list of strings
            List of tooltips. Length of the list should equal to length of languages.
        """
        tooltips = tuple(tooltips)
        self._sanity_check(tooltips, feature_name='tooltips')
        self.tooltips = tooltips

    def add_custom_coordinates(self, custom_coordinates):
        """Set custom coordinates

        By default coordinates for the languages are taken from the Glottolog database.
        If you have coordinates and want to use them, use this function.
        
        custom_coordinates: list of custom_coordinates (tuples)
            Length of the list should equal to length of languages.
        """
        custom_coordinates = tuple(custom_coordinates)
        self._sanity_check(custom_coordinates, feature_name='custom_coordinates')
        self.custom_coordinates = custom_coordinates

    def add_minimap(self, position='bottomleft', width=150, height=150, collapsed_width=25, collapsed_height=25, zoom_animation=True):
        """Add minimap

        position: str, default 'bottomleft'
        width: int, default 150
        height: int, default 150
        collapsed_width: int, default 25
        collapsed_height: int, default 25
        zoom_animation: bool, default True
            You can disable zoom animation for better performance.
        """
        self.minimap = {'position': position, 'width': width, 'height': height, 'collapsed_width': collapsed_width, 'collapsed_height': collapsed_height, 'zoom_animation': zoom_animation}

    def add_minichart(self, data):
        """Not implemented"""
        self._sanity_check(data, feature_name='minicharts')
        self.minicharts = data

    def add_rectangle(self, locations, tooltip='', popup='', color='black'):
        """Add one rectangle

        To add several rectangles, use this function several times.

        locations: list of two tuples
            Coordinates of two points to draw a rectangle.
        tooltip: str, default ''
        popups: str, default ''
        color: str, default 'black'
        """
        locations = tuple(locations)
        self.rectangles.append({'bounds': locations, 'tooltip': tooltip, 'popup': popup, 'color': color})

    def add_line(self, locations, tooltip='', popup='', color='black', smooth_factor=1.0):
        """Add one line

        To add several lines, use this function several times.

        locations: list of two tuples
            Coordinates of two points to draw a line.
        tooltip: str, default ''
        popups: str, default ''
        color: str, default 'black'
        smooth_factor: float, default 1.0
        """
        locations = tuple(locations)
        self.lines.append({'locations': locations, 'tooltip': tooltip, 'popup': popup, 'color': color, 'smooth_factor': smooth_factor})

    def add_heatmap(self, heatmap=[]):
        """Add heatmap

        heatmap: list of tuples
            Coordinates for the heatmap.
        """
        self.use_heatmap = True
        self.heatmap = tuple(heatmap)

    def _sanity_check(self, features, feature_name='corresponding lists'):
        """Checks if length of features, popups and tooltips is equal to the length of languages

        features: list
        feature_name: str, default 'corresponding list'
            feature_name is what will appear in the exception.
        """
        if len(self.languages) != len(features):
            raise LingMapError("Length of languages and {} does not match".format(feature_name))
    
    def _create_map(self):
        """Draw the map

        Gets all necessary attributes and draws everything on the map.

        Returns
        ----------
        m: folium.Map
        """
        if isinstance(self.start_location, str):
            if not self.start_location in self.start_location_mapping:
                raise LingMapError('No such start location shortcut. Try passing coordinates.')
            mapped_location_and_zoom = self.start_location_mapping[self.start_location]
            self.start_location = mapped_location_and_zoom['start_location']
            self.start_zoom = mapped_location_and_zoom['start_zoom']
        m = folium.Map(location=self.start_location, zoom_start=self.start_zoom, control_scale=self.control_scale, prefer_canvas=self.prefer_canvas)

        default_group = folium.FeatureGroup()
        markers = []
        strokes = []
        s_markers = []
        s_strokes = []
        if self.minimap:
            minimap = folium.plugins.MiniMap(**self.minimap)
            m.add_child(minimap)
        if self.rectangles:
            for rectangle in self.rectangles:
                folium.Rectangle(**rectangle).add_to(m)
        if self.lines:
            for line in self.lines:
                folium.PolyLine(**line).add_to(m)
        if self.title:
            self._create_title(m, self.title)
    
        if self.heatmap_only:
            if self.heatmap:
                self._create_heatmap(m, self.heatmap)
            #If we don't draw markers, we're done here
            return m

        if self.features:
            prepared = self._prepare_features(self.features, use_shapes=self.use_shapes)
            groups_features = prepared[0]
            data = prepared[1]

        if self.stroke_features:
            prepared = self._prepare_features(self.stroke_features, stroke=True, use_shapes=self.use_shapes)
            s_groups_features = prepared[0]
            s_data = prepared[1]
        for i, language in enumerate(self.languages):
            stroke_marker = False
            if self.custom_coordinates:
                coordinates = self.custom_coordinates[i]
            else:
                coordinates = lingtypology.glottolog.get_coordinates(language)
                if not coordinates or math.isnan(coordinates[0]) or math.isnan(coordinates[1]):
                    continue
                self.heatmap.append(coordinates)
            
            if self.features:
                color_shape = groups_features[i][1]
            else:
                color_shape = '#DEB887'

            if self.stroke_features:
                s_color = s_groups_features[i][1]
            else:
                s_color = '#000000'
                
            unified_marker = self._create_unified_marker(coordinates, color_shape, s_color)
            
            self._create_popups(unified_marker['marker'], language, i, parse_html=self.html_popups)

            if self.features and not self.numeric and self.control:
                group = groups_features[i][0]
            elif self.stroke_features and self.stroke_control:
                group = s_groups_features[i][0]
            else:
                group = default_group
                
            if self.tooltips:
                tooltip = folium.Tooltip(self.tooltips[i])
                tooltip.add_to(unified_marker['marker'])

            markers.append((unified_marker['marker'], group))
            if unified_marker['stroke']:
                strokes.append((unified_marker['stroke'], group))
            if unified_marker['s_marker']:
                s_markers.append((unified_marker['s_marker'], group))
            if unified_marker['s_stroke']:
                s_strokes.append((unified_marker['s_stroke'], group))

        #This order is important
        if s_strokes:
            [s_stroke[0].add_to(s_stroke[1]) for s_stroke in s_strokes]
        if s_markers:
            [s_mark[0].add_to(s_mark[1]) for s_mark in s_markers]
        if strokes:
            [stroke[0].add_to(stroke[1]) for stroke in strokes]
        [mark[0].add_to(mark[1]) for mark in markers]
        
        if self.features:
            if self.numeric:
                m.add_child(default_group)
                self._create_legend(m, data, title=self.legend_title, position=self.legend_position)
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
                if self.stroke_features and self.stroke_legend:
                    self._create_legend(m, s_data, title=self.stroke_legend_title, position=self.stroke_legend_position)
        else:
            m.add_child(default_group)
            
        if self.use_heatmap:
            self._create_heatmap(m, self.heatmap)

        #if lingtypology.glottolog.warnings:
        #    print('(get_coordinates) Warning: coordinates for {} not found'.format(', '.join(lingtypology.glottolog.warnings)))
        return m

    def save(self, path):
        """Save to file

        path: str
            Path to the output HTML file.
        """
        self._create_map().save(path)

    def render(self):
        """Renders the map returns it as HTML string"""
        return self._create_map().get_root().render()

def map_feature(
    languages,
    custom_coordinates=None,
    features=None,
    stroke_features=None,
    popups=None,
    tooltips=None,
    start_zoom=None,
    start_location=None,
    minimap=False,
    legend_title=None,
    legend_position=None,
    stroke_legend_title=None,
    stroke_legend_position=None,
    save_html = None
):
    """Function that tries to look like agricolamz' map.feature. Its usage is discouraged
    
    This function does not allow much customization and lacks some cool features, DON'T USE IT IF YOU CAN.
    Parameters:
    ------------
    languages: list, 
    custom_coordinates=None: list,
    features=None: list,
    stroke_features=None: list,
    popups=None: list,
    tooltips=None: list,
    start_zoom=None: int,
    start_location=None: tuple of coordinates,
    minimap=False: bool,
    legend_title=None: str,
    legend_position=None: str,
    stroke_legend_title=None: str,
    stroke_legend_position=None: str,
    V   V   V   V   V   V   V
    The function just passes the parameters as attributes to the LingMap class.
    
    If save_html is str:
        Saves under save_html name
    If None or '' or False:
        Returns html as str
    """
    m = LingMap(languages)
    if custom_coordinates:
        m.add_custom_coordinates(custom_coordinates)
    if not features is None:
        m.add_features(features)
    if not stroke_features is None:
        m.add_stroke_features(stroke_features)
    if not popups is None:
        m.add_popups(popups)
    if not tooltips is None:
        m.add_tooltips(tooltips)
    if start_zoom:
        m.start_zoom = start_zoom
    if start_location:
        m.start_location = start_location
    if minimap:
        m.add_minimap()
    if legend_title:
        m.legend_title = legend_title
    if legend_position:
        m.legend_position = legend_position
    if stroke_legend_title:
        m.stroke_legend_title = stroke_legend_title
    if stroke_legend_position:
        m.stroke_legend_position = stroke_legend_position
    if save_html:
        m.save(save_html)
    else:
        return m.render()
    
    

