"""This module draws a map"""

#Folium tools
import folium
import folium.plugins

#Branca tools
import branca.colormap
import branca.element

import jinja2
import pandas
import math
import io
import os
import re
import matplotlib.pyplot as plt
from colour import Color
from collections import deque

#Local tools
import lingtypology.glottolog

class LingMapError(Exception):
    """All special exceptions"""
    def __init__(self,value):
        self.msg = value
    def __str__(self):
        return self.msg

def gradient(iterations, color1='white', color2='green'):
    """Makes a color gradient
    
    Parameters:
    -----------
    iterations: int
        Length of gradient.
    color1: str, default 'white'
        First color.
    color2: str, default 'green'
        Second color.
    """
    color1 = Color(color1)
    colors = [color.get_hex() for color in color1.range_to(Color(color2), iterations)]
    return colors

def frange(start, stop, step):
    """range for floats"""
    while start < stop:
        yield start
        start += step

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
    base_map: folium.Map, default None
        In case you want to draw something on particular folium.Map.
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
    colormap_colors: tuple, default ('white','green')
        Default colors for the colormap.
    minicharts: list, defaule []
        List of folium.DivIcon for minicharts
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
        self.colors = ['#e6194b', '#19e6b4', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6',
                  '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8','#800000',
                  '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']
        self.shapes = ['⬤', '◼', '▲', '◯', '◻', '△', '◉', '▣', '◐', '◧', '◭', '◍','▤', '▶']
        # Map
        self.base_map = None
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
        self.stroke_legend_position = 'topright'
        # Popups
        self.languages_in_popups = True
        self.html_popups = False
        # Markers
        self.use_shapes = False
        self.radius = 7
        self.opacity = 1
        self.stroke_radius = 12
        self.stroked = True
        self.unstroked = True
        # Control
        self.control = False
        self.stroke_control = False
        self.control_position = 'topright'
        # Colormap
        self.colormap_colors = ('white', 'green')
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
        self.minicharts = []
        self.minichart_names = []
        self.marker_groups = []

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
        fill_opacity: float, default 1,
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
        try:
            al = list(zip(features, *attrs_r))
            al.sort(key=lambda element: element[0])
        except TypeError:
            #In case of different types, fall back to sorting as srt
            al = list(zip(map(str, features), *attrs_r))
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
        features = self._sort_all(features)
        if self.numeric and not stroke:
            if not all(isinstance(f, int) or isinstance(f, float) for f in features):
                try:
                    features = [int(el) for el in features]
                except ValueError:
                    features = [float(el) for el in features]
                    if all(el.is_integer() for el in features):
                        features = [int(el) for el in features]
            else:
                if isinstance(features[0], float):
                    if all(el.is_integer() for el in features):
                        features = [int(el) for el in features]

            colormap = branca.colormap.LinearColormap(colors=self.colormap_colors,
                                                      index=[features[0], features[-1]],
                                                      vmin=features[0],
                                                      vmax=features[-1],
                                                      caption=self.legend_title)
            if isinstance(features[-1], int):
                if features[-1] // 10 == 0:
                    colormap_features = list(range(features[0], features[-1])) + [features[-1]]
                else:
                    colormap_features = list(range(features[0], features[-1], features[-1] // 10))
            else:
                colormap_features = list(frange(features[0], features[-1], features[-1] / 10))
            
            groups_features = [(0, colormap(feature)) for feature in features]
            data = ''
            for cf in colormap_features:
                data += '<li><span style="background: {};opacity:0.7;"></span>{}</li>'.format(colormap(cf), cf)
        else:
            mapping = {}
            clear_features = []
            groups = []
            #Two datas are needed so that I can first try sorting as numeric, then fallback to strings
            data_as_str = []
            data_as_num = []
            for i, feature in enumerate(features):
                if feature not in clear_features:
                    clear_features.append(feature)
                    groups.append(folium.FeatureGroup(name=features[i]))
            for i, feature in enumerate(clear_features):
                mapping[feature] = (groups[i], colors[i])
                data_as_str.append((str(feature), colors[i]))
                data_as_num.append((feature, colors[i]))
            groups_features = [mapping[f] for f in features]
            try:
                data_as_num.sort()
                data = data_as_num
            except Exception:
                data_as_str.sort()
                data = data_as_str
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
                marker = self._set_marker([coordinates[0], coordinates[1]], radius=self.radius, fill_opacity=self.opacity, fill_color=color_shape)
                stroke = self._set_marker([coordinates[0], coordinates[1]], stroke=True, radius=self.radius*1.15, fill_opacity=self.opacity, fill_color='#000000')
                s_marker = self._set_marker([coordinates[0], coordinates[1]], radius=self.stroke_radius, fill_opacity=self.stroke_opacity, fill_color=s_color)
                s_stroke = self._set_marker([coordinates[0], coordinates[1]], stroke=True, radius=self.stroke_radius*1.15, fill_opacity=self.stroke_opacity, fill_color='#000000')
            else:
                marker = self._set_marker([coordinates[0], coordinates[1]], stroke=self.stroked, fill_opacity=self.opacity, fill_color=color_shape)
                s_marker = self._set_marker([coordinates[0], coordinates[1]], stroke=self.stroked, radius=self.stroke_radius, fill_opacity=self.stroke_opacity, fill_color=s_color)
        else:
            if self.use_shapes:
                marker = self._set_marker([coordinates[0], coordinates[1]], fill_color='#000000', fill_opacity=self.opacity, shape=color_shape)
            else:
                if self.unstroked:
                    marker = self._set_marker([coordinates[0], coordinates[1]], radius=self.radius, fill_opacity=self.opacity, fill_color=color_shape)
                    stroke = self._set_marker([coordinates[0], coordinates[1]], stroke=True, radius=self.radius*1.15, fill_opacity=self.opacity, fill_color='#000000')
                else:
                    marker = self._set_marker([coordinates[0], coordinates[1]], stroke=self.stroked, radius=self.radius, fill_opacity=self.opacity, fill_color=color_shape)
        return {'marker': marker, 'stroke': stroke, 's_marker': s_marker, 's_stroke': s_stroke}

    def add_features(self, features, radius=7, opacity=1, numeric=False, control=False, use_shapes=False):
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
        self.opacity = opacity
        if numeric:
            self.numeric = True
        else:
            self.numeric = False
        if control:
            self.control = True
        if use_shapes:
            self.use_shapes = True

    def add_stroke_features(self, features, radius=12, opacity=1, numeric=False, control=False):
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
        self.stroke_opacity = opacity
        if numeric:
            self.s_numeric = True
        else:
            self.s_numeric = False
        if control:
            self.stroke_control = True
        self.stroke_radius = radius

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

    def add_minicharts(self, *minicharts, typ='pie', size=0.6, names=None,
                       textprops=None, labels=False, startangle=90, colors=[], bar_width=1):
        """Create minicharts using maplotlib
        
        How it works:
        * Draw plots using matplotlib.
        * Save it as SVG but catch the stream.
        * Create markers with SVG DivIcon.
        * Create popups with data from the plots.
        """
        if names is None:
            if all(isinstance(minichart, pandas.Series) for minichart in minicharts):
                names = [serie.name for serie in minicharts]
            else:
                raise LingMap('You shound either pass names or use pandas.Series')
        self.minichart_names = names
        self.minicharts_data = minicharts
        self.popups = []
        
        fig = plt.figure(figsize=(size, size))
        
        if typ == 'pie':
            fig.patch.set_alpha(0)
        elif typ == 'bar':
            fig.patch.set_visible(False)
        else:
            raise LingMapError('{}: unknown type of chart. You can use either "pie" or "bar"')
        
        ax = fig.add_subplot(111)
        
        for minichart in list(zip(*minicharts)):
            sizes = minichart
            if colors:
                self.colors = colors
            else:
                colors = self.colors
            if typ == 'pie':
                if labels:
                    #I'm not allowed to simply pass sizes! I have to take percentages and then turn them back to sizes. Matplotlib sucks :(
                    ax.pie(
                        sizes, colors=colors, startangle=startangle,
                        autopct=lambda p: '{}'.format(int(p * sum(sizes)//100)),
                        textprops=textprops
                    )
                else:
                    ax.pie(sizes, colors=colors, startangle=startangle)
            elif typ == 'bar':
                ax.bar(self.minichart_names, height=sizes, color=colors, width=bar_width)
                ax.axis('off')
            buff = io.StringIO()
            plt.savefig(buff, format='SVG')
            buff.seek(0)
            plt.cla()

            svg = buff.read()
            size = (float(re.findall('height="(.*?)pt"', svg)[0]), float(re.findall('width="(.*?)pt"', svg)[0]))
            center = ((size[0] / 2)*1.31, (size[1] / 2)*1.31)

            self.minicharts.append(folium.DivIcon(html=svg.replace('\n', ''), icon_anchor=center))
            popup = '<br>'
            for name, value in zip(names, minichart):
                popup += '{}: {}<br>'.format(name, str(value))
            self.popups.append(popup)
        plt.clf()
        plt.close()
    
    def add_overlapping_features(self, marker_groups, radius=7, radius_increment=4, mapping=None):
        self.marker_groups = marker_groups
        self.radius = radius
        self.radius_increment = radius_increment
        self.custom_mapping = mapping

    def _sanity_check(self, features, feature_name='corresponding lists'):
        """Checks if length of features, popups and tooltips is equal to the length of languages

        features: list
        feature_name: str, default 'corresponding list'
            feature_name is what will appear in the exception.
        """
        if len(self.languages) != len(features):
            raise LingMapError("Length of languages and {} does not match".format(feature_name))
    
    def create_map(self):
        """Draw the map

        Gets all necessary attributes and draws everything on the map.
        
        How it works:
        * Set up start location and zoom if start_location is passed as shortcut.
        * Create folium.Map object using [self.start_location, zoom_start=self.start_zoom,
            control_scale=self.control_scale, prefer_canvas=self.prefer_canvas]
        * Create default_group (folium.FeatureGroup)
        * Declare lists: markers, strokes, s_markers, s_strokes
        * Check whether minimap, rectangles, lines and title are here and draw them.
        * If the user sets self.heatmap_only to True, draw it and return the map.
            {{first ending}}
        * If user passes minicharts:
            * Walk in self.languages:
                * Apply custom coordinates or the ones from Glottolog.
                * Set folium.Marker with plot SVG as folium.DivIcon
                * Create popups with links to Glottolog (if necessary) and
                    data from plots.
                * Draw the logend using names from plots and colors.
                * Return the map.
                {{ second ending }}
        * If features are given, prepare them (_prepare_features). This includes:
            * Creating folium.FeatureGroup.
            * Creating data for legend.
            * Storing info on features as list of tuples (len = 2)
                * The first element: color (HEX) of shape (Unicode)
                * The second element: folium.FeatureGroup
        * If stroke features are given, prepare them as well.
        * Walk in languages:
            * Apply custom coordinates or the ones from Glottolog.
            * Create unified marker using:
                coordinates, color/shape for features and color for stroke features.
                Unified marker is a dict that consists of information necessary
                to draw 1-4 markers (more look in docstring for _create_unified_marker.
            * Create popup for the marker (_create_popups method).
            * Create tooltips.
            * Append the unified_marker to the the folium.FeatureGroup.
        * If features are numeric:
            * Add them to the default FeatureGroup.
            * Draw the legend (_create_legend).
        * If not:
            * Add them to proper FeatureGroups.
            * If LayerControl if asked for, draw it.
            * Draw the legend (_create_legend).
        * If heatmap is asked for, draw it (_create_heatmap).
        * Return the map.
        {{true ending}}

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
        if self.base_map:
            m = self.base_map
        else:
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

        if self.minicharts:
            #we'll draw minicharts separately
            for i, language in enumerate(self.languages):
                if self.custom_coordinates:
                    coordinates = self.custom_coordinates[i]
                else:
                    coordinates = lingtypology.glottolog.get_coordinates(language)
                    if not coordinates or math.isnan(coordinates[0]) or math.isnan(coordinates[1]):
                        continue
                marker = folium.Marker(coordinates, self.minicharts[i])

                if self.languages_in_popups or self.minichart_names:
                    popup_contents = ''
                    if self.languages_in_popups:
                        popup_href = '''<a href="https://glottolog.org/resource/languoid/id/{}" onclick="this.target='_blank';">{}</a>'''
                        popup_contents += popup_href.format(lingtypology.glottolog.get_glot_id(language), language)
                    if self.popups:
                        marker.add_child(folium.Popup(popup_contents + self.popups[i]))
                    else:
                        marker.add_child(folium.Popup(popup_contents))
                if self.tooltips:
                    tooltip = folium.Tooltip(self.tooltips[i])
                    tooltip.add_to(marker)
                m.add_child(marker)
                
            if self.minichart_names:
                legend_data = ''
                for i, name in enumerate(self.minichart_names):
                    legend_data += '<li><span style="background: {};opacity:0.7;"></span>{}</li>\n'.format(self.colors[i], self.minichart_names[i])
                self._create_legend(m, legend_data, title=self.legend_title, position=self.legend_position)
            return m
        
        if self.marker_groups:
            #Separately too
            if self.custom_mapping:
                color_mapping = self.custom_mapping
            else:
                color_mapping = {}
                i = 0
                for mark in self.marker_groups:
                    for feat in mark:
                        if not feat in color_mapping:
                            color_mapping[feat] = self.colors[i]
                            i += 1
            for i, language in enumerate(self.languages):
                if self.custom_coordinates:
                    coordinates = self.custom_coordinates[i]
                else:
                    coordinates = lingtypology.glottolog.get_coordinates(language)
                    if not coordinates or math.isnan(coordinates[0]) or math.isnan(coordinates[1]):
                        continue
                
                if len(self.marker_groups[i]) == 1:
                    radius = self.radius
                else:
                    radius = len(self.marker_groups[i]) * self.radius_increment
                
                opacity = self.opacity
                for marker_data in self.marker_groups[i]:
                    marker = self._set_marker(coordinates, stroke=self.stroked, radius=radius, fill_opacity=self.opacity, fill_color=color_mapping[marker_data])
                    radius -= self.radius_increment
                    if self.tooltips:
                        tooltip = folium.Tooltip(self.tooltips[i])
                        tooltip.add_to(marker)
                    self._create_popups(marker, language, i, parse_html=self.html_popups)
                    markers.append(marker)
            deque(map(m.add_child, markers))
            legend_data = ''
            for feature in color_mapping:
                legend_data += '<li><span style="background: {};opacity:0.7;"></span>{}</li>\n'.format(color_mapping[feature], feature)
            self._create_legend(m, legend_data, title=self.legend_title, position=self.legend_position)
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
        self.create_map().save(path)

    def render(self):
        """Renders the map returns it as HTML string"""
        return self.create_map().get_root().render()

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
