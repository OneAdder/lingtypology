"""APIs for work Wals and Phoible. Requires Internet connection."""
import pandas
import urllib.request as ur
import lingtypology.glottolog


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
                print(self._get_citation(feature))
            wals_feature = self._get_wals_data(feature)
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

'''
class Phoible(object):
    """Phoible

    show_citation: bool, default True
        Whether to print the citation.
    """
    show_citation = True
    citation =  """
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
                """
    def get_df(self):
        """Get data from Phoible in pandas.DataFrame format.

        Returns pandas.DataFrame
            Headers: 'iso', 'language', 'coordinates', 'phonemes', 'consonants', 'tones', 'vowels'.
        """
        if self.show_citation:
            print(self.citation)
        phoible_url = 'https://raw.githubusercontent.com/clld/phoible/master/data/phoible-aggregated.tsv'
        original_df = pandas.read_csv(phoible_url, delimiter='\t', header=0)
        
        df = pandas.DataFrame(columns=['iso', 'language', 'coordinates', 'phonemes', 'consonants', 'tones', 'vowels'])
        df.iso = original_df.LanguageCode
        df.language = [glottolog.get_by_iso(iso) for iso in list(original_df.LanguageCode)]
        df.coordinates = zip(list(original_df.Latitude), list(original_df.Longitude))
        df.phonemes = original_df.Phonemes.astype(int)
        df.consonants = original_df.Consonants.astype(int)
        df.tones = original_df.Tones.astype(int)
        df.vowels = original_df.Vowels.astype(int)
        return df

    def get_json(self):
        """Get data from Phoible in pandas.DataFrame format.

        Returns dict
            Keys: 'iso', 'language', 'coordinates', 'phonemes', 'consonants', 'tones', 'vowels'.
        """
        df = self.get_df()
        js = {header: list(df[header]) for header in list(df)}
        return js
'''

#print(Wals('1a').get_json())
#print(list(Phoible().get_json()))
