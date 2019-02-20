"""APIs for work Wals and Phoible. Requires Internet connection."""
import pandas
import urllib.request as ur


class Wals(object):
    """Wals

    show_citation: bool, default True
        Whether to print the citation.
    """
    show_citation = True

    def __init__(self, features):
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
            Headers: 'wals code', 'language', 'latitude', 'longitude', 'genus', 'family', 'area'.
        """
        wals_url = 'http://wals.info/feature/1A.tab'
        df = pandas.read_csv(wals_url, delimiter='\t', skiprows=7)
        df = df.drop('value', 1)
        df = df.drop('description', 1)
        df = df.rename(columns={'name': 'language'})
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
            print('(Wals) Warning: cannot read Wals feature ' + feature)
        else:
            return df_feature[['wals code','description']]

    def _get_citation(self, feature):
        """Loads citation from Wals

        Parameter feature: str
            Name of the Wals page.

        Returns str
        """
        wals_url = 'http://wals.info/feature/{}.tab'.format(feature)
        wals_page = ur.urlopen(wals_url)
        _citation = 'Citation for feature {}:\n{}\n'
        citation = _citation.format(feature, '\n'.join(wals_page.read().decode('utf-8').split('\n')[:5]))
        return citation

    def get_df(self):
        """Get data from Wals in pandas.DataFrame format.

        Returns pandas.DataFrame
            Headers: 'wals code', 'language', 'latitude', 'longitude', 'genus', 'family', 'area', [[name of the page1]], [[name of the page2]], ...
            Names of the pages start with '_'.
        """
        features = self.features
        if isinstance(features, str):
            features = (features,)
        df = self._get_wals_template()
        for feature in features:
            feature = feature.upper()
            if self.show_citation:
                print(self._get_citation(feature))
            wals_feature = self._get_wals_data(feature)
            wals_feature = wals_feature.rename(columns={'description': '_' + feature})
            df = pandas.merge(df, wals_feature, on="wals code")
        return df

    def get_json(self):
        """Get data from Wals in JSON format.

        Returns dict
            Keys: 'wals code', 'language', 'latitude', 'longitude', 'genus', 'family', 'area', [[name of the page1]], [[name of the page2]], ...
            Names of the pages start with '_'.
        """
        df = self.get_df()

        js = {}
        for header in list(df):
            if not header == 'latitude' and not header == 'longitude':
                js[header] = list(df[header])

        coordinates = list(zip(list(df.latitude), list(df.longitude)))
        js['coordinates'] = coordinates
        return js


class Phoible(object):
    """Phoible

    show_citation: bool, default True
        Whether to print the citation.
    """
    show_citation = True
    citation =  '''
Moran, Steven & McCloy, Daniel & Wright, Richard (eds.) 2014. PHOIBLE Online. Leipzig: Max Planck Institute for Evolutionary Anthropology. (Available online at http://phoible.org, Accessed on ...)
A BibTeX entry for LaTeX users is
@book{phoible,
address   = {Leipzig},
editor    = {Steven Moran and Daniel McCloy and Richard Wright},
publisher = {Max Planck Institute for Evolutionary Anthropology},
title     = {PHOIBLE Online},
url       = {http://phoible.org/},
year      = {2014}
}
                '''
    def get_df(self):
        """Get data from Phoible in pandas.DataFrame format.

        Returns pandas.DataFrame
            Headers: 'InventoryID', 'Source', 'LanguageCode',
            'LanguageName', 'Trump', 'LanguageFamilyRoot',
            'LanguageFamilyGenus', 'Country', 'Area', 'Population',
            'Latitude', 'Longitude', 'Phonemes', 'Consonants', 'Tones', 'Vowels'.
        """
        if self.show_citation:
            print(self.citation)
        phoible_url = 'https://raw.githubusercontent.com/clld/phoible/master/data/phoible-aggregated.tsv'
        df = pandas.read_csv(phoible_url, delimiter='\t', header=0)
        df.LanguageName = df.LanguageName.str.capitalize()
        return df

    def get_json(self):
        """Get data from Phoible in pandas.DataFrame format.

        Returns pandas.DataFrame
            Keys: 'InventoryID', 'Source', 'LanguageCode',
            'LanguageName', 'Trump', 'LanguageFamilyRoot',
            'LanguageFamilyGenus', 'Country', 'Area', 'Population',
            'Latitude', 'Longitude', 'Phonemes', 'Consonants', 'Tones', 'Vowels'.
        """
        df = self.get_df()
        js = {}
        for header in list(df):
            if not header == 'Latitude' and not header == 'Longitude':
                js[header] = list(df[header])
        coordinates = list(zip(list(df.Latitude), list(df.Longitude)))
        return js

#print(list(Wals('1a').get_json()))
#print(list(Phoible().get_json()))
