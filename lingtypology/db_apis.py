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
        self.features_list = [
            '1A', '2A', '3A', '4A', '5A', '6A', '7A', '8A', '9A', '10A', '10B', '11A', '12A', '13A', '14A',
            '15A', '16A', '17A', '18A', '19A', '20A', '21A', '21B', '22A', '23A', '24A', '25A', '25B', '26A',
            '27A', '28A', '29A', '30A', '31A', '32A', '33A', '34A', '35A', '36A', '37A', '38A', '39A', '39B',
            '40A', '41A', '42A', '43A', '44A', '45A', '46A', '47A', '48A', '49A', '50A', '51A', '52A', '53A',
            '54A', '55A', '56A', '57A', '58A', '58B', '59A', '60A', '61A', '62A', '63A', '64A', '65A', '66A',
            '67A', '68A', '69A', '70A', '71A', '72A', '73A', '74A', '75A', '76A', '77A', '78A', '79A', '79B',
            '80A', '81A', '81B', '82A', '83A', '84A', '85A', '86A', '87A', '88A', '89A', '90A', '90B', '90C',
            '90D', '90E', '90F', '90G', '91A', '92A', '93A', '94A', '95A', '96A', '97A', '98A', '99A', '100A',
            '101A', '102A', '103A', '104A', '105A', '106A', '107A', '108A', '108B', '109A', '109B', '110A',
            '111A', '112A', '113A', '114A', '115A', '116A', '117A', '118A', '119A', '120A', '121A', '122A',
            '123A', '124A', '125A', '126A', '127A', '128A', '129A', '130A', '130B', '131A', '132A', '133A',
            '134A', '135A', '136A', '136B', '137A', '137B', '138A', '139A', '140A', '141A', '142A', '143A',
            '143B', '143C', '143D', '143E', '143F', '143G', '144A', '144B', '144C', '144D', '144E', '144F',
            '144G', '144H', '144I', '144J', '144K', '144L', '144M', '144N', '144O', '144P', '144Q', '144R',
            '144S', '144T', '144U', '144V', '144W', '144X', '144Y'
        ]

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
    
    @property
    def citation(self):
        cit = ''
        for feature in self.features:
            cit += self._get_citation(feature.upper()) + '\n'
        return cit

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
        show_citation: bool, default True
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

    def get_df(self, strip_na=[]):
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
            df.fillna('~N/A~', inplace=True)

            if merged_df.empty:
                languages = []
                for LID in df.LID:
                    try:
                        languages.append(lingtypology.glottolog.get_by_glot_id((self.mapping[str(LID)])))
                    except KeyError:
                        warnings.warn('Unable to find Glottocode for' + str(LID))
                        languages.append('')
                languages_df = pandas.DataFrame()
                languages_df = languages_df.assign(language=languages)
                merged_df = languages_df.join(df)
            else:
                merged_df = pandas.merge(merged_df, df, on='LID')
        merged_df.fillna('~N/A~', inplace=True)
        for column in strip_na:
            merged_df = merged_df[merged_df[column] != '~N/A~']
        return merged_df

    def get_json(self, strip_na=[]):
        """Get data from Autotyp in JSON format.

        Returns dict
            Keys: 'Language', 'LID', [[features columns]]
        """
        df = self.get_df(strip_na=strip_na)
        js = {header:list(df[header]) for header in list(df)}
        return js


class AfBo(object):
    """AfBo database of borrowed affixes"""
    def __init__(self, *features):
        """init

        features: list
            List of features that the user wants to access.
        show_citation: bool, default True
            Whether to display citation for Autoyp or not.
        citation:
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
            language_recipient = self.afbo_data['Recipient name'],
            language_donor = self.afbo_data['Donor name'],
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

        
class Sails(object):
    """Sails dataset

    It's from CLLD, so it's really complicated.
    """
    def __init__(self, *features):
        """init

        1) Setting attributes:
            features: list
                User-defined features.
            show_citation: bool, default True
                Whether to show the citation.
            citation: str
                Citation.
        2) Ripping the archive from the website and setting:
            languages: pandas.DataFrame
                CLLD table with info on languages.
            parameters: pandas.DataFrame
                CLLD table with info on features.
            values: pandas.DataFrame
                CLLD table with values of the features for different languages.
        3) For users:
            features_list: list
                List of all available features.
            features_descriptions: pandas.DataFrame
                DataFrame with features (abbreviations) and their descriptions.
        """
        self.features = features
        self.show_citation = True
        self.citation = "You probably should cite it, but I don't understand how. Please, consult https://sails.clld.org/"
        
        response = requests.get('https://cdstar.shh.mpg.de/bitstreams/EAEA0-0A75-A1F1-F344-0/SAILS_dataset.cldf.zip')
        with zipfile.ZipFile(io.BytesIO(response.content)) as thezip:
            for info in thezip.infolist():
                if info.filename == 'parameters.csv':
                    with thezip.open(info) as thefile:
                        parameters = thefile.read().decode('utf-8')
                elif info.filename == 'languages.csv':
                    with thezip.open(info) as thefile:
                        languages = thefile.read().decode('utf-8')
                elif info.filename == 'values.csv':
                    with thezip.open(info) as thefile:
                        values = thefile.read().decode('utf-8')
        self.languages = pandas.read_csv(io.StringIO(languages), sep=',', header=0)
        self.parameters = pandas.read_csv(io.StringIO(parameters), sep=',', header=0)
        self.values = pandas.read_csv(io.StringIO(values), sep=',', header=0)

        self.features_list = sorted(list(set(self.parameters.ID)))
        self.features_descriptions = pandas.DataFrame({'Feature': self.parameters.ID, 'Description': self.parameters.Name})

    def feature_descriptions(self, *features):
        """Get the description for a particular feature."""
        descriptions = []
        for i, feature in enumerate(features):
            descriptions += list(self.parameters[self.parameters.ID == feature].Name)
        return pandas.DataFrame({'Feature': features, 'Description': descriptions})

    def get_df(self):
        """Get data from SAILS in pandas.DataFrame format.

        Returns pandas.DataFrame
            Headers: 'Language', 'Coordinates', [[feature 1]], [[feature 1 human_readable]], [[feature 2]], ...
        """
        if self.show_citation:
            print(self.citation)
        merged_df = pandas.DataFrame()
        for feature in self.features:
            feature = feature.upper()
            df = self.values[self.values.Parameter_ID == feature]
            new_df = pandas.DataFrame()
            #languages <- select all language names for language ids in the table with values
            languages = [list(self.languages[self.languages['ID'] == lang_id].Name)[0] for lang_id in df['Language_ID']]
            #latitudes <- select latitudes and longitudes from the language table and zip them
            latitudes = [list(self.languages[self.languages['Name'] == lang].Latitude)[0] for lang in languages]
            longitudes = [list(self.languages[self.languages['Name'] == lang].Longitude)[0] for lang in languages]
            coordinates = list(zip(latitudes, longitudes))
            new_df['language'] = languages
            new_df['coordinates'] = coordinates
            new_df[feature] = list(df.Value)
            new_df[feature + '_desc'] = list(df.Value.replace(['0', '1', '?'], ['No', 'Yes', '?']))
            if merged_df.empty:
                merged_df = new_df
            else:
                merged_df = pandas.merge(merged_df, new_df, how='outer', on=['language', 'coordinates'])
        merged_df.fillna('~N/A~', inplace=True)
        return merged_df

    def get_json(self):
        """Get data from SAILS in JSON format.

        Returns dict
            Keys: 'Language', 'Coordinates', [[feature 1]], [[feature 1 human_readable]], [[feature 2]], ...
        """
        df = self.get_df()
        js = {header:list(df[header]) for header in list(df)}
        return js


class Phoible(object):
    """Phoible"""
    def __init__(self, subset='all'):
        """init

        show_citation: bool, default True
            Whether to display citation for Autoyp or not.
        citation:
            Citation for Phoible.
        subset: str, default 'all'
            Subset of Phoible (all, only UPSID, only SPA etc.)
        subsets_list: list
            List of available subsets of Phoible.
        """
        self.show_citation = True
        self.citation = 'Moran, Steven & McCloy, Daniel (eds.) 2019.\nPHOIBLE 2.0.\n' + \
                        'Jena: Max Planck Institute for the Science of Human History.\n' + \
                        '(Available online at http://phoible.org, Accessed on {}.)'.format(datetime.now().strftime('%Y-%m-%d'))
        self.subsets_list = ['all', 'UPSID', 'SPA', 'AA', 'PH', 'GM', 'RA', 'SAPHON']
        
        self.subset = subset
        self.inventories = pandas.read_csv('https://phoible.org/inventories.csv', sep=',', header=0)
        self.languages = pandas.read_csv('https://phoible.org/languages.csv', sep=',', header=0)
        #if include_everything:
        #    self.raw_data = pandas.read_csv('https://raw.githubusercontent.com/phoible/dev/master/data/phoible.csv', sep=',', header=0, low_memory=False)

    def get_df(self, strip_na=[]):
        """Get data from Phoible in pandas.DataFrame format.

        Returns pandas.DataFrame
            Headers: 'contribution_name', 'language', 'coordinates', 'glottocode', 'macroarea', 'consonants', 'vowels', 'source', 'inventory_page'
        """
        if self.show_citation:
            print(self.citation)
        inventories = self.inventories[['name', 'count_consonant', 'count_tone', 'count_vowel', 'language_pk', 'source_url']]
        if self.subset != 'all':
            subset = self.subset.upper()
            inventories = inventories[inventories.name.str.contains(subset)]
        languages = self.languages[['id', 'latitude', 'longitude', 'macroarea', 'name', 'pk']]
        languages = languages.rename(columns={'name': 'language'})
        pre_df = pandas.merge(languages, inventories, left_on='pk', right_on='language_pk')
        df = pandas.DataFrame({
            'contribution_name': pre_df.name,
            'language': pre_df.language,
            'coordinates': list(zip(pre_df.latitude, pre_df.longitude)),
            'glottocode': pre_df.id,
            'macroarea': pre_df.macroarea,
            'phonemes': pre_df.count_consonant + pre_df.count_vowel,
            'consonants': pre_df.count_consonant,
            'vowels': pre_df.count_vowel,
            'tones': pre_df.count_tone,
            'source': pre_df.source_url,
            'inventory_page': 'https://phoible.org/languages/' + pre_df.id
        })
        df.fillna('~N/A~', inplace=True)
        for column in strip_na:
            df = df[df[column] != '~N/A~']
        return df

    def get_json(self, strip_na=[]):
        """Get data from Phoible in JSON format.

        Returns dict
            Keys: 'contribution_name', 'language', 'coordinates', 'glottocode', 'macroarea', 'consonants', 'vowels', 'source', 'inventory_page'
        """
        df = self.get_df(strip_na=strip_na)
        js = {header:list(df[header]) for header in list(df)}
        return js
    
#print(Wals('1a', '2a').get_df())
#print(Wals('1a', '2a').general_citation)
#print(Wals('1a', '2a').citation)
#print(Wals().features_list)
#print(list(Autotyp('Gender', 'Agreement').get_df()))
#print(Autotyp().features_list)
#print(list(AfBo().afbo_data))
#print(AfBo().features_list)
#print(AfBo('adverbializer', 'case: non-locative peripheral case').get_df())
#print(Sails('ICU10', 'ICU11').get_df())
#print(Sails().features_descriptions)
#print(Sails().feature_descriptions('ICU10', 'ICU11'))
#print(Phoible().get_df(strip_na=['tones']))
