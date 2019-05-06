"""APIs for work Wals and Autotyp."""
import pandas
import urllib
import lingtypology.glottolog
import warnings
import json
import re

ur = urllib.request

class Wals(object):
    """Wals

    show_citation: bool, default True
        Whether to print the citation.
    """
    show_citation = True

    def __init__(self, *features):
        """init

        features: list of strings
            Wals pages you want to use.
        """
        self.features = features

    def _get_wals_template(self):
        """Makes pandas.DaraFrame with all the data except for the pages.

        Returns:
        ---------
        df: pandas.DataFrame
            Headers: 'wals code', 'language', 'genus', 'family', 'area', 'coordinates'.
        """
        wals_url = 'http://wals.info/feature/1A.tab'
        df = pandas.read_csv(wals_url, delimiter='\t', skiprows=7)
        coordinates = zip(list(df.latitude), list(df.longitude))
        df.drop('latitude', axis=1, inplace=True)
        df.drop('longitude', axis=1, inplace=True)
        df = df.assign(coordinates=pandas.Series(coordinates))
        df.drop('value', axis=1, inplace=True)
        df.drop('description', axis=1, inplace=True)
        df.rename(columns={'name': 'language'}, inplace=True)
        return df

    def _get_wals_data(self, feature):
        """Loads data from Wals

        Parameter feature: str
            Name of the Wals page.

        Returns pandas.DataFrame
            Headers: 'wals code', 'description'.
        """
        wals_url = 'http://wals.info/feature/{}.tab'.format(feature)
        try:
            df_feature = pandas.read_csv(wals_url, delimiter='\t', skiprows=7)
        except:
            warnings.warn('(Wals) Warning: cannot read Wals feature ' + feature)
        else:
            return df_feature[['wals code','description']]

    def _get_citation(self, feature):
        """Loads citation from Wals

        Parameter feature: str
            Name of the Wals page.

        Returns str
        """
        wals_url = 'http://wals.info/feature/{}.tab'.format(feature)
        try:
            wals_page = ur.urlopen(wals_url)
        except urllib.error.HTTPError:
            warnings.warn('No such feature in WALS')
            return
        _citation = 'Citation for feature {}:\n{}\n'
        citation = _citation.format(feature, '\n'.join(wals_page.read().decode('utf-8').split('\n')[:5]))
        return citation

    def get_df(self):
        """Get data from Wals in pandas.DataFrame format.

        Returns pandas.DataFrame
            Headers: 'wals code', 'language', 'genus', 'family', 'area', 'coordinates', [[name of the page1]], [[name of the page2]], ...
            Names of the pages start with '_'.
        """
        features = self.features
        if isinstance(features, str):
            features = (features,)
        df = self._get_wals_template()
        for feature in features:
            feature = feature.upper()
            if self.show_citation:
                citation = self._get_citation(feature)
                if citation:
                    print(citation)
            wals_feature = self._get_wals_data(feature)
            if not wals_feature is None:
                wals_feature = wals_feature.rename(columns={'description': '_' + feature})
                df = pandas.merge(df, wals_feature, on="wals code")
        return df

    def get_json(self):
        """Get data from Wals in JSON format.

        Returns dict
            Keys: 'wals code', 'language', 'genus', 'family', 'area', 'coordinates', [[name of the page1]], [[name of the page2]], ...
            Names of the pages start with '_'.
        """
        df = self.get_df()
        js = { header:list(df[header]) for header in list(df)}
        return js

class Autotyp(object):
    """Autotyp"""
    def __init__(self, table):
        self.table = table
        self.show_citation = True
        with open('autotyp_lang_mapping.json', 'r', encoding='utf-8') as f:
            self.mapping = json.load(f)

    def _show_citation(self):
        print(
            'Bickel, Balthasar, Johanna Nichols, Taras Zakharko, '
            'Alena Witzlack-Makarevich, Kristine Hildebrandt, Michael Rießler, '
            'Lennart Bierkandt, Fernando Zúñiga & John B. Lowe. '
            '2017. The AUTOTYP typological databases. '
            'Version 0.1.0 https://github.com/autotyp/autotyp-data/tree/0.1.0'
        )

    def tables_list(self):
        github_page = ur.urlopen('https://github.com/autotyp/autotyp-data/tree/master/data').decode('utf-8')
        return re.findall('title="(.*?)\.csv"')

    def get_df(self):
        if self.show_citation:
            self._show_citation()
            

    
#print(Wals('1af', '2a').get_df())
print(Autotyp.tables_list())
