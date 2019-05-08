"""APIs for work Wals and Autotyp."""
import pandas
import requests
import urllib.error
import lingtypology.glottolog
import warnings
import json
import re
import os
import io
import zipfile
from datetime import datetime

module_directory = os.path.dirname(os.path.realpath(__file__))

class Wals(object):
    """Wals

    show_citation: bool, default True
        Whether to print the citation.
    general_citation: str<
        General citation of the whole WALS.
    """

    def __init__(self, *features):
        """init

        features: list of strings
            Wals pages you want to use.
        """
        self.features = features
        self.show_citation = True
        self.general_citation = 'Dryer, Matthew S. & Haspelmath, Martin (eds.) 2013.\n' + \
        'The World Atlas of Language Structures Online.\n' + \
        'Leipzig: Max Planck Institute for Evolutionary Anthropology.\n' + \
        '(Available online at http://wals.info, Accessed on {}.)'.format(datetime.now().strftime('%Y-%m-%d'))

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
        except urllib.error.HTTPError:
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
        wals_page = requests.get(wals_url)
        if wals_page.status_code == 404:
            warnings.warn('No such feature in WALS')
            return
        _citation = 'Citation for feature {}:\n{}\n'
        citation = _citation.format(feature, '\n'.join(wals_page.content.decode('utf-8').split('\n')[:5]))
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
        js = {header:list(df[header]) for header in list(df)}
        return js


class Autotyp(object):
    """Autotyp"""
    def __init__(self, *tables):
        """init

        tables: list
            List of tables that the user wants to access.
        show_citation: bool
            Whether to display citation for Autoyp or not.
        citation:
            Citation for Autotyp.
        mapping: dict
            Mapping from Autotyp LID to Glottocode.
        features_list: list
            List of available tables from Autotyp.
        """
        self.tables = tables
        self.show_citation = True
        self.citation = 'Bickel, Balthasar, Johanna Nichols, Taras Zakharko,\n' + \
                        'Alena Witzlack-Makarevich, Kristine Hildebrandt, Michael Rießler,\n' + \
                        'Lennart Bierkandt, Fernando Zúñiga & John B. Lowe.\n' + \
                        '2017. The AUTOTYP typological databases.\n' + \
                        'Version 0.1.0 https://github.com/autotyp/autotyp-data/tree/0.1.0'

    @property
    def mapping(self):
        """Get mapping from Autotyp LID to Glottocode"""
        with open(
            os.path.join(
                module_directory,
                'autotyp_lang_mapping.json'
            ),
            'r', encoding='utf-8'
        ) as f:
            mapping = json.load(f)
        return mapping
    
    @property
    def features_list(self):
        """List of available Autotyp tables"""
        github_page = requests.get('https://github.com/autotyp/autotyp-data/tree/master/data').content.decode('utf-8')
        return re.findall('title="(.*?)\.csv"', github_page)

    def get_df(self):
        """Get data from Autotyp in pandas.DataFrame format.

        Returns pandas.DataFrame
            Headers: 'Language', 'LID', [[features columns]]
        """
        if not self.tables:
            warnings.warn('No tables given. To get list of available features use Autotyp.features_list')
            return
        if self.show_citation:
            print(self.citation)

        merged_df = pandas.DataFrame()
        for table in self.tables:
            try:
                df = pandas.read_csv('https://raw.githubusercontent.com/autotyp/autotyp-data/master/data/{}.csv'.format(table))
            except urllib.error.HTTPError:
                warnings.warn('Unable to find table ' + table)
                continue
            df.fillna('N/A', inplace=True)

            if merged_df.empty:
                languages = []
                for LID in df.LID:
                    try:
                        languages.append(lingtypology.glottolog.get_by_glot_id((self.mapping[str(LID)])))
                    except KeyError:
                        warnings.warn('Unable to find Glottocode for' + str(LID))
                        languages.append('')
                languages_df = pandas.DataFrame()
                languages_df = languages_df.assign(Language=languages)
                merged_df = languages_df.join(df)
            else:
                merged_df = pandas.merge(merged_df, df, on='LID')
        merged_df.fillna('', inplace=True)
        return merged_df

    def get_json(self):
        """Get data from Autotyp in JSON format.

        Returns dict
            Keys: 'Language', 'LID', [[features columns]]
        """
        df = self.get_df()
        js = {header:list(df[header]) for header in list(df)}
        return js


class AfBo(object):
    """AfBo database of borrowed affixes"""
    def __init__(self, *features):
        """init

        features: list
            List of features that the user wants to access.
        show_citation: bool
            Whether to display citation for Autoyp or not.
        citaion:
            Citation for AfBo.
        features_list: list
            List of available tables from AfBo.
        """
        self.features = features
        self.show_citation = True
        self.citation = 'Seifart, Frank. 2013.\n' + \
                        'AfBo: A world-wide survey of affix borrowing.\n' + \
                        'Leipzig: Max Planck Institute for Evolutionary Anthropology.\n' + \
                        '(Available online at http://afbo.info, Accessed on {}.)'.format(datetime.now().strftime('%Y-%m-%d'))

        response = requests.get('https://cdstar.shh.mpg.de/bitstreams/EAEA0-59C8-38F2-28DC-0/afbo_pair.csv.zip')
        with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
            for info in thezip.infolist():
                if info.filename.endswith('.csv'):
                    with thezip.open(info) as thefile:
                        csv_data = thefile.read().decode('utf-8')
        self.afbo_data = pandas.read_csv(io.StringIO(csv_data), sep=',', header=0)
        self.afbo_data.fillna('0', inplace=True)

        self.features_list = list(self.afbo_data)[10:]

    def get_df(self):
        """Get data from AfBo in pandas.DataFrame format.

        Returns pandas.DataFrame
            Headers: 'Recipient_name', 'Donor_name', [[feature1]], [[feature2]], ...
        """
        if not self.features:
            warnings.warn('No tables given. To get list of available features use AfBo.features_list')
            return
        if self.show_citation:
            print(self.citation)

        df = pandas.DataFrame()
        df = df.assign(
            Recipient_name = self.afbo_data['Recipient name'],
            Donor_name = self.afbo_data['Donor name'],
            reliability = self.afbo_data['reliability'],
        )

        for feature in self.features:
            try:
                df[feature] = self.afbo_data[feature]
            except KeyError:
                warnings.warn('No feature named {}. To get list of available features use AfBo.features_list'.format(feature))
        return df

    def get_json(self):
        """Get data from AfBo in JSON format.

        Returns dict
            Keys: 'Recipient_name', 'Donor_name', [[feature1]], [[feature2]], ...
        """
        df = self.get_df()
        js = {header:list(df[header]) for header in list(df)}
        return js
        



#print(Wals('1a', '2a').get_df())
#print(Wals('1a', '2a').general_citation)
#print(list(Autotyp('Gender', 'Agreement').get_df()))
#print(Autotyp().features_list)
#print(list(AfBo().afbo_data))
#print(AfBo().features_list)
#print(AfBo('adverbializer', 'case: non-locative peripheral case').get_df())
