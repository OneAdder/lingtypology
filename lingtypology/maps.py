import folium
import folium.plugins

import branca.colormap
import branca.element

import jinja2
import pandas
import json
import math
import io
import os
import re
import random
import matplotlib.pyplot as plt
import colour
import collections

import lingtypology.glottolog
from lingtypology.lingtypology_exceptions import LingMapError

MODULE_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + os.path.sep

def merge(*maps, autoset_legends=True):
    """Merge several LingMap objects
    
    Parameters
    -----------
    *maps: list of LingMap
        List of LingMap objects.
    autoset_legends: bool, default True
        If set to True, legends will automatically move to free spaces
    
    Returns
    -------
    m: lingtypology.maps.LingMap
    """
    def generate_new():
        new_legend_position = ''
        for legend_position in legend_positions:
            if not legend_position in occupied_legend_positions:
                new_legend_position = legend_position
                break
        if new_legend_position:
            return new_legend_position
        else:
            return 'topright'
    legend_positions = ['topright', 'topleft', 'bottomright',
                        'bottomleft', 'bottom', 'right', 'left']
    occupied_legend_positions = set()
    legend_id = maps[0]._legend_id
    for i, m in enumerate(maps):
        if not m == maps[0]:
            legend_id += m._legend_id
            m.base_map = maps[i - 1].create_map()
            m.legend_id = legend_id
        if autoset_legends:
            if m.legend_position in occupied_legend_positions:
                m.legend_position = generate_new()
            if m.stroke_legend_position in occupied_legend_positions:
                m.stroke_legend_position = generate_new()
            occupied_legend_positions.add(m.legend_position)
            occupied_legend_positions.add(m.stroke_legend_position)
    return m

def get_elevations(languages):
    """Get elevation data for list of languages.
    
    Parameters
    -----------
    languages: list of str
        Languages from Glottolog.
    
    Returns
    -------
    elevations: list of coordinates
    """
    with open(MODULE_DIRECTORY + 'language_elevation_mapping.json') as f:
        j = json.load(f)
    elevations = []
    not_okay = []
    for language in languages:
        try:
            elevations.append(j[language])
        except KeyError:
            elevations.append('')
            not_okay.append(language)
    if not_okay:
        print('Elevations for these languages were not found: ' + ', '.join(list(set(not_okay))))
    return elevations

def gradient(iterations, color1='white', color2='green'):
    """Makes a color gradient.
    
    Parameters
    -----------
    iterations: int
        Length of gradient.
    color1: str, default 'white'
        First color.
    color2: str, default 'green'
        Second color.
    
    Returns
    -------
    colors: list of str
        List of HEX-colors with #.
    """
    color1 = colour.Color(color1)
    colors = [
        color.get_hex() \
            for color in color1.range_to(colour.Color(color2), iterations)
    ]
    return colors

def _frange(start, stop, step):
    """range for floats"""
    while start < stop:
        yield start
        start += step

class LingMap(object):
    """Lingtypology map object.
    
    Parameters
    ----------
    languages: list of strings, default []
        A list of languages.
        
        The language names should correspond to their names from Glottolog unless you use *add_custom_coordinates* method. Instead of language names you could use Glottocodes (language ID in Glottolog). In this case you need to set *glottocode* parameter to true.
        
    glottocodes: bool, default False
        Whether to treat languages as Glottocodes.
    
    Attributes
    ----------
    tiles: str, default 'OpenStreetMap'
        Tiles for the map.
        
        You can use one of these tiles (list of tiles is borrowed from the Folium Documentation):

        -   "OpenStreetMap"

        -   "Mapbox Bright" (Limited levels of zoom for free tiles)

        -   "Mapbox Control Room" (Limited levels of zoom for free tiles)

        -   "Stamen" (Terrain, Toner, and Watercolor)

        -   "Cloudmade" (Must pass API key)

        -   "Mapbox" (Must pass API key)

        -   "CartoDB" (positron and dark_matter)

        -   or pass the custum URL.
    start_location: (float, float), default (0, 0)
        Coordinates of the start location for the map (latitude, longitude) or a text shortcut.
    
        List of available shortcuts:
        
        -   "Central Europe"
        
        -   "Caucasus"
        
        -   "Australia & Oceania"
        
        -   "Papua New Guinea"
        
        -   "Africa"
        
        -   "Asia"
        
        -   "North America"
        
        -   "Central America"
        
        -   "South America"
        
    start_zoom: int, default 2
        Initial zoom level.
        
        Bypassed if you are using a start_location shortcut.
    control_scale: bool, default True
        Whether to add control scale.
    base_map: folium.Map, default None
        In case you want to draw something on particular folium.Map.
    colors: list of html codes for colors
        Colors that represent features.
        You can either use the default colors or set yours.
    stroke_colors: list of html codes for colors
        Colors that represent additional (stroke) features.
        You can either use the default colors or set yours.
    shapes: list of characters
        If you use shapes instead of colors, you can either use the default shapes or set yours.
        Shapes are Unicode symbols.
    
    prefer_canvas: bool, default False
        Use canvas instead of SVG.
        
        If set to True, the map may be more responsive in case you have a lot of markers.
    base_map: folium.Map, default None
        In case you want to draw something on particular folium.Map.
    title: str, default None
        You can add a title to the map.
    legend: bool, default True
        Whether to add legend for features (add_features method).
    stroke_legend: bool, default True.
        Whether to add legend for stroke features (add_stroke_features method).
    legend_title: str, default 'Legend'
        Legend title.
    stroke_legend_title: str, default 'Legend'
        Stroke legend title.
    legend_position: str, default 'bottomright'
        Legend position.
        
        Available values: 'right', 'left', 'top', 'bottom', 'bottomright', 'bottomleft', 'topright', 'topleft'.
    stroke_legend_position: str, default 'bottomleft'
        Stroke legend position.
        
        Available values: 'right', 'left', 'top', 'bottom', 'bottomright', 'bottomleft', 'topright', 'topleft'.
    colors: list of html codes for colors (str), default None
        Colors that represent features.
        
        You can either use the 20 default colors(if None) or set yours(else).
    stroke_colors: list of html codes for colors (str), default None
        Colors that represent stroke features.
        
        You can either use the 20 default colors(if None) or set yours(else).
    colormap_colors: tuple, default ('white', 'green')
        Colors for the colormap.
    shapes: list of characters (str)
        If you use shapes instead of colors, you can either use the default shapes or set yours. Shapes are Unicode symbols.
    stroked: bool, default True
        Whether to add stroke to markers.
    unstroked: bool, default True
        If set to True, circle marker will merge if you zoom out without stroke between them. It multiplies the number of markers by 2. For better performance set it to False.
    control: bool, default False
        Whether to add LayerControls and group by features.
    stroke_control: bool, default False
        Whether to add LayerControls and group by stroke features.
    control_position: str, default 'topright'
        Position of LayerControls.
        
        May be 'topleft', 'topright', 'bottomleft' or 'bottomright'.
    """
    '''
    To understand how unstroked works looks see the example below.

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
    '''
    
    def __init__(self, languages=[], glottocode=False):
        """__init__

        Sets self.languages turning it into a tuple.
        If no languages are given, sets self.heatmap_only to true.
        If glottocode is True, languages will not be converted to glottocodes
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
        self.glottocode = glottocode
        self.warnings_enabled = False
        # Feature representation
        self.stroke_colors = [
            '#ffffff', '#000000', '#800000',
            '#BC8F8F', '#FFE4C4', '#6495ED',
            '#4682B4', '#FF6347', '#778899',
            '#40E0D0', '#00FFFF', '#F08080',
            '#6495ED', '#FF7F50', '#D2691E',
            '#7FFF00', '#5F9EA0', '#DEB887',
            '#A52A2A', '#8A2BE2', '#0000FF',
        ]
        self.colors = [
            '#e6194b', '#19e6b4', '#ffe119',
            '#4363d8', '#f58231', '#911eb4',
            '#46f0f0', '#f032e6', '#bcf60c',
            '#fabebe', '#008080', '#e6beff',
            '#9a6324', '#fffac8', '#800000',
            '#aaffc3', '#808000', '#ffd8b1',
            '#000075', '#808080', '#ffffff',
        ]
        self.shapes = ['⬤', '◼', '▲', '◯', '◻', '△', '◉',
                       '▣', '◐', '◧', '◭', '◍','▤', '▶']
        # Map
        self.tiles = 'OpenStreetMap'
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
        self.numeric = False
        self.s_numeric = False
        self.colormap_colors = ('white', 'green')
        self.stroke_colormap_colors = ('white', 'red')
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
    
    def _check_and_generate_colors(self):
        """Checks whether amount of some unique features is larger that the amount of colors"""
        if self.features:
            colors = len(self.colors)
            features = len(set(self.features))
            
            if colors < features:
                new_colors = [
                    '#{:06x}'.format(random.randint(0, 256**3)) \
                        for x in range(features-colors)
                ]
                self.colors += new_colors
        
        if self.stroke_features:
            stroke_colors = len(self.stroke_colors)
            stroke_features = len(set(self.stroke_features))
            
            if stroke_colors < stroke_features:
                new_colors = [
                    '#{:06x}'.format(random.randint(0, 256**3)) \
                        for x in range(stroke_features-stroke_colors)
                ]
                self.stroke_colors += new_colors
        
    def _get_coordinates(self, language, i):
        """Get coordinates either from:
            self.custom_coordinates or
            self.languages as language names or
            self.languages as glottocode.
        
        Parameters:
        -----------
        language: str
            Either language name or glottocode.
        i: int
            Iteration of the cicle.
        
        Returns: tuple of two ints (coordinates).
        """
        if self.custom_coordinates:
            coordinates = self.custom_coordinates[i]
        else:
            if self.glottocode:
                coordinates = \
                    lingtypology.glottolog.get_coordinates_by_glot_id(language)
            else:
                coordinates = \
                    lingtypology.glottolog.get_coordinates(language)
        if not coordinates \
            or math.isnan(coordinates[0]) \
            or math.isnan(coordinates[1]):
            return
        else:
            return coordinates

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
        popup_href = \
            '<a ' \
                'href="https://glottolog.org/resource/languoid/id/{}" ' \
                '''onclick="this.target='_blank';"''' \
            '>' \
                '{}'\
            '</a>'\
            '<br>'
        href_link = lingtypology.glottolog.get_glot_id(language) \
            if not self.glottocode \
            else language
        href_content = language \
            if not self.glottocode \
            else lingtypology.glottolog.get_by_glot_id(language)
        popup_href = popup_href.format(href_link, href_content) \
            if href_link \
            else href_content
        if self.languages_in_popups:
            if self.popups:
                if parse_html:
                    raise LingMapError(
                        'It is impossible to add both language links' \
                        'and large HTML strings.\n' \
                        'You can either not use html_popups option ' \
                        'or set ling_map_object.languages_in_popups = False.'
                    )
                popup = folium.Popup(popup_href + self.popups[i])
            else:
                popup = folium.Popup(popup_href)
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
        with open(MODULE_DIRECTORY + 'legend.html', 'r', encoding='utf-8') as f:
            template = f.read()
        template = jinja2.Template(template)
        template = template.render(
            data=legend_data, position=position, title=title,
            use_shapes=self.use_shapes, legend_id=self._legend_id
        )
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

    def _create_title(self, m, title, position='top'):
        """Creates title and adds it to the map

        m: folium.Map
            The map.
        title: str
            Title.
        """
        with open(MODULE_DIRECTORY + 'legend.html', 'r', encoding='utf-8') as f:
            template = f.read()
        template = jinja2.Template(template)
        template = template.render(position=position, title=title,
                                   legend_id=self._legend_id, it_is_title=True)
        template = '{% macro html(this, kwargs) %}' + template + '{% endmacro %}'
        macro = branca.element.MacroElement()
        macro._template = branca.element.Template(template)
        m.get_root().add_child(macro)
        self._legend_id += 1

    def _set_marker(self,
                    location,
                    radius = 7,
                    fill = True,
                    stroke = False,
                    weight = 1,
                    fill_opacity = 1,
                    color = '#000000',
                    fill_color = '#DEB887',
                    shape = ''):
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
            div = folium.DivIcon(
                html='<div style="font-size: 170%">' + str(shape) + '</div>'
            )
            marker = folium.Marker(location=location, icon=div)
        else:
            marker = folium.CircleMarker(
                location = location,
                radius = radius,
                fill = fill,
                stroke = stroke,
                weight = weight,
                fill_opacity = fill_opacity,
                color = color,
                fill_color = fill_color
            )
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
        attrs = [self.languages, self.popups,
                 self.tooltips, self.custom_coordinates]
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
            #In case of different types, fall back to sorting as str
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
    
    def _make_colormap(self, features, colormap_colors):
        def round_up(a, digits=0):
            if digits is None:
                return a
            n = 10** - digits
            return round(math.ceil(a / n) * n, digits)
        def round_down(a, digits=0):
            if digits is None:
                return a
            n = 10** - digits
            return round(math.floor(a / n) * n, digits)
        def how_round(n):
            if n / 10000 > 1:
                return -4
            elif n / 1000 > 1:
                return -3
            elif n / 100 > 1:
                return -2
            elif n / 10 > 1:
                return -1
            elif n > 1 and isinstance(n, float):
                return 0
            return None
            
        #Round features so that they look handsome
        digits = how_round(features[-1])
        minimum = round_down(features[0], digits)
        maximum = round_up(features[-1], digits)
        
        colormap = branca.colormap.LinearColormap(
            colors = colormap_colors,
            index = [minimum, maximum],
            vmin = minimum,
            vmax = maximum,
        )
        
        if isinstance(features[-1], int):
            if features[-1] // 10 == 0:
                step = 1
                colormap_features = list(range(minimum, maximum)) + [maximum]
            else:
                step = maximum // 10
                colormap_features = list(range(minimum, maximum, step))
        else:
            step = maximum / 10
            colormap_features = list(_frange(minimum, maximum, step))

        # Crazy stuff below draws SVGs with color gradient
        groups_features = [(0, colormap(feature)) for feature in features]
        color_data = ''
        text = ''
        i = 0
        for ind, cf in enumerate(colormap_features):
            color_data += '<line x1="0" y1="{pos}" x2="20" y2="{pos}"' \
                'style="stroke:{color};stroke-width:3;" />'.format(
                    pos=i, color=colormap(cf)
                )
            i += 1
            if not ind == 0:
                text += '<text x="5" y="{pos}" dx="0" dy="0ex">- {text}</text>'.format(
                    pos=i, text=cf
                )
            if not ind + 1 == len(colormap_features):
                gr = [
                    colormap(f) \
                        for f in _frange(
                            cf, colormap_features[ind + 1], step / 20
                        )
                ][1:-2]
                for c in gr:
                    i += 1
                    color_data += '<line x1="0" y1="{pos}" x2="20" y2="{pos}"' \
                        'style="stroke:{color};stroke-width:3;" />'.format(
                            pos=i, color=c
                        )
        
        gradient_templ = '<svg height="' + str(i) + '" width="20">{}</svg>'
        text_templ = '<svg height="' + str(i) + '" width="50">{}</svg>'
        data = \
            gradient_templ.format(color_data) + \
            text_templ.format(text)
        return data, groups_features

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
        if use_shapes:
            colors = self.shapes
        elif stroke:
            colors = self.stroke_colors
        else:
            colors = self.colors
            
        numeric = self.s_numeric if stroke else self.numeric
        colormap_colors = self.stroke_colormap_colors \
            if stroke \
            else self.colormap_colors
            
        features = self._sort_all(features)
        if numeric:
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
            data, groups_features = \
                self._make_colormap(features, colormap_colors)
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
                data.append((feature, colors[i]))
            groups_features = [mapping[f] for f in features]
            html = \
                '<li>' \
                    '<span ' \
                        'style="' \
                            'color: #000000; ' \
                            'text-align: center; ' \
                            'opacity:0.7; ' \
                        '">\n' \
                            '{}\n' \
                    '</span>' \
                        '{}' \
                '</li>' \
                    if use_shapes \
                    else \
                        '<li><span ' \
                            'style="background: {};opacity:0.7;"' \
                        '></span>{}</li>'
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
                marker = self._set_marker(
                    [coordinates[0], coordinates[1]],
                    radius = self.radius,
                    fill_opacity = self.opacity,
                    fill_color = color_shape
                )
                stroke = self._set_marker(
                    [coordinates[0], coordinates[1]],
                    stroke = True,
                    radius = self.radius * 1.15,
                    fill_opacity = self.opacity,
                    fill_color = '#000000'
                )
                s_marker = self._set_marker(
                    [coordinates[0], coordinates[1]],
                    radius = self.stroke_radius,
                    fill_opacity = self.stroke_opacity,
                    fill_color = s_color
                )
                s_stroke = self._set_marker(
                    [coordinates[0], coordinates[1]],
                    stroke = True,
                    radius = self.stroke_radius * 1.12,
                    fill_opacity = self.stroke_opacity,
                    fill_color = '#000000'
                )
            else:
                marker = self._set_marker(
                    [coordinates[0], coordinates[1]],
                    stroke = self.stroked,
                    fill_opacity = self.opacity,
                    fill_color = color_shape
                )
                s_marker = self._set_marker(
                    [coordinates[0], coordinates[1]],
                    stroke = self.stroked,
                    radius = self.stroke_radius,
                    fill_opacity = self.stroke_opacity,
                    fill_color = s_color
                )
        else:
            if self.use_shapes:
                marker = self._set_marker(
                    [coordinates[0], coordinates[1]],
                    fill_color = '#000000',
                    fill_opacity = self.opacity,
                    shape = color_shape
                )
            else:
                if self.unstroked:
                    marker = self._set_marker(
                        [coordinates[0], coordinates[1]],
                        radius = self.radius,
                        fill_opacity = self.opacity,
                        fill_color = color_shape
                    )
                    stroke = self._set_marker(
                        [coordinates[0], coordinates[1]],
                        stroke = True,
                        radius = self.radius * 1.15,
                        fill_opacity = self.opacity,
                        fill_color = '#000000'
                    )
                else:
                    marker = self._set_marker(
                        [coordinates[0], coordinates[1]],
                        stroke = self.stroked,
                        radius = self.radius,
                        fill_opacity = self.opacity,
                        fill_color = color_shape
                    )
        return {'marker': marker, 'stroke': stroke,
                's_marker': s_marker, 's_stroke': s_stroke}
    
    def add_custom_coordinates(self, custom_coordinates):
        """Set custom coordinates.

        By default cooordinates for the languages
        are taken from the Glottolog database. If you have coordinates and
        want to use them, use this function.

        It could be useful if you are using data from a dataset which
        provides coordinates and you do not need to rely on the Glottolog
        data.
        
        Parameters
        ----------
        custom_coordinates: list of coordinates (tuples)
            Length of the list should equal to length of languages.
        """
        custom_coordinates = tuple(custom_coordinates)
        self._sanity_check(custom_coordinates, feature_name='custom_coordinates')
        self.custom_coordinates = custom_coordinates

    def add_features(self, features, radius=7, opacity=1, colors=None,
                     numeric=False, control=False, use_shapes=False):
        """Add features.
        
        Parameters
        ----------
        features: list of strings
            List of features.
            
            Length of the list should equal to length of languages.
            Amount of features should be equal to the amount of languages.
            By default, if you add features, a legend will appear.
            To shut it down set legend attribute to False.
            To change the title of the legend use legend_title attribute.
            To change legend position use use legend_position attribute.
        radius: int, default 7
            Marker radius.
        opacity: float, default 1
            Marker opacity: a number between 0(invisible) and 1(not transparent).
        colors: list of html codes for colors (str), default None
            Colors that represent features. You can either use the 20 default
            colors(if None) or set yours(else).
        numeric: bool, default False
            Whether to assign different color to each feature (False), or
            to assign a color from colormap (True). You can set it to True
            only in case your features are numeric and stroke features are
            not given. To change the default colors of the color scale use
            colormap_colors attribute.
        control: bool, default False
            Whether to add LayerControls to the map.
            It allows interactive turning on/off given features.
        use_shapes: bool, default False
            Whether to use shapes instead of colors. This option allows to
            represent features as shapes. Shapes are Unicode charaters. You
            can replace or add to default symbols by changing shapes
            attribute. If colors are not a viable option for you, you can
            set this option to True.
        """
        features = tuple(features)
        self._sanity_check(features, feature_name='features')
        self.features = features
        self.radius = radius
        self.opacity = opacity
        if colors:
            self.colors = colors
        
        self.numeric = numeric
        self.control = control
        self.use_shapes = use_shapes

    def add_stroke_features(self, features, radius=12, opacity=1,
                            colors=None, numeric=False, control=False):
        """Add stroke features.

        This function assigns features to strokes of markers.
        
        Parameters
        ----------
        features: list of strings
            List of additional features. Amount of features should be equal
            to the amount of languages. By default, if you add stroke
            features, a legend will appear. To shut it down set
            stroke_legend attribute to False. To change the title of
            the legend use stroke_legend_title attribute. To change
            legend position use use stroke_legend_position attribute.
        opacity: float, default 1
            Marker opacity: a number between 0(invisible) and 1(not transparent).
        colors: list of html codes for colors (str), default None
            Colors that represent stroke features. You can either use the 20 default
            colors(if None) or set yours(else).
        radius: int, default 12
            Marker radius.
        control: bool, default False
            Whether to add LayerControls to the map.
            It allows interactive turning on/off given features.
        """
        features = tuple(features)
        self._sanity_check(features, feature_name='stroke features')
        self.stroke_features = features
        self.stroke_radius = radius
        self.stroke_opacity = opacity
        if colors:
            self.stroke_colors = colors
        
        self.s_numeric = numeric
        self.stroke_control = control
    
    def add_overlapping_features(self, marker_groups,
                                 radius=7, radius_increment=4,
                                 colors=None, mapping=None):
        """Add overlapping features.
        
        For example, if you want to draw on map whether language 'is ergative', 'is slavic', 'is spoken in Russia'.
        It will draw several markers of different size for each location.
        
        Parameters
        ----------
        features: list of lists
            List of features. Amount of features should be equal to the
            amount of languages.
        radius: int, default 7
            Radius of the smallest circle.
        radius_increment: int, default 4
            Step by which the size of the marker for each feature will be
            incremented.
        colors: list of html codes for colors (str), default None
            Colors that represent features. You can either use the 20 default
            colors(if None) or set yours(else).
        mapping: dict, default None
            Mapping for the legend.
        """
        self.marker_groups = marker_groups
        self.radius = radius
        self.radius_increment = radius_increment
        if colors:
            self.colors = colors
        self.custom_mapping = mapping

    def add_minicharts(self, *minicharts,
                       typ='pie', size=0.6,
                       names=None, textprops=None,
                       labels=False, startangle=90,
                       colors=None, bar_width=1):
        """Create minicharts using maplotlib.
        
        Parameters
        ----------
        *minicharts: list-like objects
            Data for minicharts. Two list-like objects.
        typ: str, default pie
            Type of the minicharts. Either pie or bar.
        size: float
            Size of the minicharts.
        texprops: dict, default None
            Textprops for Matplotlib.
        labels: bool, default False
            Whether to display labels.
        colors: list, default None
            Minicharts colors.
        startange: int, default 90
            Start angle of pie-charts (pie-charts only).
        """
        '''
        How it works:
        * Draw plots using matplotlib.
        * Save it as SVG but catch the stream.
        * Create markers with SVG DivIcon.
        * Create popups with data from the plots.
        '''
        if names is None:
            if all(isinstance(minichart, pandas.Series) for minichart in minicharts):
                names = [serie.name for serie in minicharts]
            else:
                raise LingMapError('You shound either pass names or use pandas.Series')
        self.minichart_names = names
        self.minicharts_data = minicharts
        self.popups = []
        
        fig = plt.figure(figsize=(size, size))
        
        if typ == 'pie':
            fig.patch.set_alpha(0)
        elif typ == 'bar':
            fig.patch.set_visible(False)
        else:
            raise LingMapError(
                '{}: unknown type of chart.\n' \
                'You can use either "pie" or "bar"'.format(typ)
            )
        
        ax = fig.add_subplot(111)
        
        for minichart in list(zip(*minicharts)):
            sizes = minichart
            if colors:
                self.colors = colors
            else:
                colors = self.colors
            if typ == 'pie':
                if labels:
                    ax.pie(
                        sizes, colors=colors, startangle=startangle,
                        textprops=textprops,
                        labels=sizes,
                        labeldistance=0.2
                    )
                else:
                    ax.pie(sizes, colors=colors, startangle=startangle)
            elif typ == 'bar':
                ax.bar(self.minichart_names, height=sizes,
                       color=colors, width=bar_width)
                ax.axis('off')
            buff = io.StringIO()
            plt.savefig(buff, format='SVG')
            buff.seek(0)
            plt.cla()

            svg = buff.read()
            size = (float(re.findall('height="(.*?)pt"', svg)[0]),
                    float(re.findall('width="(.*?)pt"', svg)[0]))
            #This is magic
            center = ((size[0] / 2)*1.31, (size[1] / 2)*1.31)

            self.minicharts.append(
                folium.DivIcon(html=svg.replace('\n', ''), icon_anchor=center)
            )
            popup = ''
            for name, value in zip(names, minichart):
                popup += '{}: {}<br>'.format(name, str(value))
            self.popups.append(popup)
        plt.clf()
        plt.close()

    def add_heatmap(self, heatmap=[]):
        """Add heatmap.
        
        Parameters
        ----------
        heatmap: list of tuples
            Coordinates for the heatmap.
        """
        self.use_heatmap = True
        self.heatmap = tuple(heatmap)

    def add_popups(self, popups, parse_html=False, glottolog_links=True):
        """Add popups to markers.
        
        Parameters
        ----------
        popups: list of strings
            List of popups. Length of the list should equal to length of languages.
        parse_html: bool, default False
            By default (False) you can add small pieces of html code.
            If you need to add full html pages to popups, you need to set the option to True.
        glottolog_links: bool, default True
            Whether to include links to Glottolog in popups.
        """
        popups = tuple(popups)
        self._sanity_check(popups, feature_name='popups')
        self.popups = popups
        self.html_popups = parse_html
        self.languages_in_popups = glottolog_links \
            if not parse_html else False

    def add_tooltips(self, tooltips):
        """Add tooltips to markers.
        
        Parameters
        ----------
        tooltips: list of strings
            List of tooltips. Length of the list should equal to length of languages.
        """
        tooltips = tuple(tooltips)
        self._sanity_check(tooltips, feature_name='tooltips')
        self.tooltips = tooltips

    def add_minimap(self, position='bottomleft', width=150, height=150,
                    collapsed_width=25, collapsed_height=25, zoom_animation=True):
        """Add minimap.
        
        Parameters
        ----------
        position: str, default 'bottomleft'
        width: int, default 150
        height: int, default 150
        collapsed_width: int, default 25
        collapsed_height: int, default 25
        zoom_animation: bool, default True
            You can disable zoom animation for better performance.
        """
        self.minimap = {
            'position': position, 'width': width,
            'height': height,
            'collapsed_width': collapsed_width,
            'collapsed_height': collapsed_height,
            'zoom_animation': zoom_animation
        }

    def add_rectangle(self, locations, tooltip='', popup='', color='black'):
        """Add one rectangle.

        To add several rectangles, use this method several times.
        
        Parameters
        ----------
        locations: list of two tuples
            Coordinates of two points to draw a rectangle.
        tooltip: str, default ''
        popups: str, default ''
        color: str, default 'black'
        """
        locations = tuple(locations)
        self.rectangles.append({'bounds': locations, 'tooltip': tooltip,
                                'popup': popup, 'color': color})

    def add_line(self, locations, tooltip='',
                 popup='', color='black', smooth_factor=1.0):
        """Add one line.

        To add several lines, use this method several times.
        
        Parameters
        ----------
        locations: list of two tuples
            Coordinates of two points to draw a line.
        tooltip: str, default ''
        popups: str, default ''
        color: str, default 'black'
        smooth_factor: float, default 1.0
        """
        locations = tuple(locations)
        line = {'locations': locations, 'color': color,
                'smooth_factor': smooth_factor}
        if tooltip:
            line['tooltip'] = tooltip
        if popup:
            line['popup'] = popup
        self.lines.append(line)

    def _sanity_check(self, features, feature_name='corresponding lists'):
        """Checks if length of features, popups and tooltips is equal to the length of languages

        features: list
        feature_name: str, default 'corresponding list'
            feature_name is what will appear in the exception.
        """
        if len(self.languages) != len(features):
            raise LingMapError(
                'Length of languages and ' \
                '{} does not match'.format(feature_name))
    
    def create_map(self):
        """Create the map.
        
        To display the map in Jupyter Notebook, use this method.
        
        Returns
        ----------
        m: folium.Map
        """
        '''
        How it works:
        * Set up start location and zoom if start_location is passed as shortcut.
        * Create folium.Map object using [self.start_location, zoom_start=self.start_zoom,
            control_scale=self.control_scale, prefer_canvas=self.prefer_canvas]
        * Create default_group (folium.FeatureGroup)
        * Declare lists: markers, strokes, s_markers, s_strokes
        * Check whether minimap, rectangles, lines and title are here and draw them.
        * If the user sets self.heatmap_only to True, draw it and return the map.
            {{ first ending }}
        * If user passes minicharts:
            * Walk in self.languages:
                * Apply custom coordinates or the ones from Glottolog.
                * Set folium.Marker with plot SVG as folium.DivIcon
                * Create popups with links to Glottolog (if necessary) and
                    data from plots.
                * Draw the logend using names from plots and colors.
                * Return the map.
            {{ second ending }}
        * If user passes overlapping_features (LingMap().marker_groups):
            * If color_mapping is not given, make it.
            * Walk in languages:
                * Get coordinates if not given.
                * Set markers, popups and tooltips.
            * Create legend.
            {{ third ending }}
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
        '''
        self._check_and_generate_colors()
        
        if isinstance(self.start_location, str):
            if not self.start_location in self.start_location_mapping:
                raise LingMapError(
                    'No such start location shortcut. Try passing coordinates.'
                )
            mapped_location_and_zoom = \
                self.start_location_mapping[self.start_location]
            self.start_location = \
                mapped_location_and_zoom['start_location']
            self.start_zoom = \
                mapped_location_and_zoom['start_zoom']

        if self.base_map:
            m = self.base_map
        else:
            m = folium.Map(
                location=self.start_location,
                zoom_start=self.start_zoom,
                control_scale=self.control_scale,
                prefer_canvas=self.prefer_canvas,
                tiles=self.tiles
            )

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
                coordinates = self._get_coordinates(language, i)
                if not coordinates:
                    continue
                marker = folium.Marker(coordinates, self.minicharts[i])

                self._create_popups(marker, language, i,
                                    parse_html=self.html_popups)
                if self.tooltips:
                    tooltip = folium.Tooltip(self.tooltips[i])
                    tooltip.add_to(marker)
                m.add_child(marker)
                
            if self.minichart_names and self.legend:
                legend_data = ''
                for i in range(len(self.minichart_names)):
                    legend_data += \
                        '<li>' \
                            '<span style="background: {};opacity:0.7;">' \
                            '</span>' \
                            '{}' \
                        '</li>\n'.format(
                            self.colors[i], self.minichart_names[i]
                        )
                self._create_legend(m, legend_data, title=self.legend_title,
                                    position=self.legend_position)
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
                coordinates = self._get_coordinates(language, i)
                if not coordinates:
                    continue
                
                if len(self.marker_groups[i]) == 1:
                    radius = self.radius
                else:
                    radius = len(self.marker_groups[i]) * self.radius_increment
                
                for marker_data in self.marker_groups[i]:
                    marker = self._set_marker(
                        coordinates, stroke=self.stroked, radius=radius,
                        fill_opacity=self.opacity,
                        fill_color=color_mapping[marker_data]
                    )
                    radius -= self.radius_increment
                    if self.tooltips:
                        tooltip = folium.Tooltip(self.tooltips[i])
                        tooltip.add_to(marker)
                    self._create_popups(marker, language, i,
                                        parse_html=self.html_popups)
                    markers.append(marker)

            collections.deque(map(m.add_child, markers))
            
            if self.legend:
                legend_data = ''
                for feature in color_mapping:
                    legend_data += \
                        '<li>' \
                            '<span style="background: {};opacity:0.7;">' \
                            '</span>' \
                            '{}' \
                        '</li>\n'.format(color_mapping[feature], feature)
                self._create_legend(m, legend_data, title=self.legend_title,
                                    position=self.legend_position)
            return m

        if self.features:
            prepared = self._prepare_features(
                self.features, use_shapes=self.use_shapes
            )
            groups_features = prepared[0]
            data = prepared[1]

        if self.stroke_features:
            prepared = self._prepare_features(
                self.stroke_features, stroke=True, use_shapes=self.use_shapes
            )
            s_groups_features = prepared[0]
            s_data = prepared[1]

        for i, language in enumerate(self.languages):
            stroke_marker = False
            coordinates = self._get_coordinates(language, i)
            if not coordinates:
                continue
            
            self.heatmap.append(coordinates)
            
            color_shape = groups_features[i][1] \
                if self.features \
                else self.colors[0]
            
            s_color = s_groups_features[i][1] \
                if self.stroke_features \
                else self.stroke_colors[0]
                
            unified_marker = \
                self._create_unified_marker(
                    coordinates, color_shape, s_color
                )
            
            self._create_popups(
                unified_marker['marker'], language,
                i, parse_html=self.html_popups
            )

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
            collections.deque((s_stroke[0].add_to(s_stroke[1]) for s_stroke in s_strokes))
        if s_markers:
            collections.deque((s_mark[0].add_to(s_mark[1]) for s_mark in s_markers))
        if strokes:
            collections.deque((stroke[0].add_to(stroke[1]) for stroke in strokes))
        collections.deque((mark[0].add_to(mark[1]) for mark in markers))
        
        if self.features:
            if self.numeric or self.s_numeric:
                m.add_child(default_group)
                if self.numeric:
                    self._create_legend(m, data, title=self.legend_title,
                                        position=self.legend_position)
                if self.s_numeric:
                    self._create_legend(
                        m, s_data,
                        title=self.stroke_legend_title,
                        position=self.stroke_legend_position,
                    )
            else:
                if self.control:
                    collections.deque((m.add_child(fg[0]) for fg in groups_features))
                    folium.LayerControl(
                        collapsed=False,
                        position=self.control_position
                    ).add_to(m)
                elif self.stroke_control:
                    collections.deque((m.add_child(fg[0]) for fg in s_groups_features))
                    folium.LayerControl(
                        collapsed=False,
                        position=self.control_position
                    ).add_to(m)
                else:
                    m.add_child(default_group)
                
                if self.legend:
                    self._create_legend(
                        m, data, title=self.legend_title,
                        position=self.legend_position
                    )
                if self.stroke_features and self.stroke_legend:
                    self._create_legend(
                        m, s_data, title=self.stroke_legend_title,
                        position=self.stroke_legend_position
                    )
        else:
            m.add_child(default_group)
            
        if self.use_heatmap:
            self._create_heatmap(m, self.heatmap)

        if lingtypology.glottolog.warnings and self.warnings_enabled:
            print(
                '(get_coordinates) '
                'Warning: coordinates for '
                '{} not found'.format(
                    ', '.join(
                        lingtypology.glottolog.warnings
                    )
                )
            )
        return m

    def save(self, path):
        """Save as html.
        
        Parameters
        ----------
        path: str
            Path to the output HTML file.
        """
        self.create_map().save(path)

    def render(self):
        """Renders the map returns it as HTML string.
        
        Returns
        -------
        str
        """
        return self.create_map().get_root().render()
    
    def save_static(self, fname=None):
        """Save the map as PNG.
        
        Experimental function. Requires additional Python package Selenium and additional application Geckodriver.
        
        Parameters
        ----------
        fname: str, default None
            Path to the output PNG file.
            If None, the method will return PNG as bytes.
        
        Returns
        -------
        bytes
        """
        mappa = self.create_map()
        try:
            png = mappa._to_png()
        except Exception:
            print(
                'It seems that GeckoDriver is not installed.\n'
                'Method "save_static" requires it.\n'
                'You could find it here:\n'
                'https://github.com/mozilla/geckodriver'
            )
        else:
            if fname:
                with open(fname, 'wb') as f:
                    f.write(png)
            else:
                return png
