import pandas
import urllib.request as ur


class Wals(object):
    show_citation = True
    features_set = ("1A", "2A", "3A", "4A", "5A", "6A", "7A", "8A", "9A", "10A", "10B", "11A",
                    "12A", "13A", "14A", "15A", "16A", "17A", "18A", "19A", "20A", "21A", "21B",
                    "22A", "23A", "24A", "25A", "25B", "26A", "27A", "28A", "29A", "30A", "31A",
                    "32A", "33A", "34A", "35A", "36A", "37A", "38A", "39A", "39B", "40A", "41A",
                    "42A", "43A", "44A", "45A", "46A", "47A", "48A", "49A", "50A", "51A", "52A",
                    "53A", "54A", "55A", "56A", "57A", "58A", "58B", "59A", "60A", "61A", "62A",
                    "63A", "64A", "65A", "66A", "67A", "68A", "69A", "70A", "71A", "72A", "73A",
                    "74A", "75A", "76A", "77A", "78A", "79A", "79B", "80A", "81A", "81B", "82A",
                    "83A", "84A", "85A", "86A", "87A", "88A", "89A", "90A", "90B", "90C", "90D",
                    "90E", "90F", "90G", "91A", "92A", "93A", "94A", "95A", "96A", "97A", "98A",
                    "99A", "100A", "101A", "102A", "103A", "104A", "105A", "106A", "107A",
                    "108A", "108B", "109A", "109B", "110A", "111A", "112A", "113A", "114A",
                    "115A", "116A", "117A", "118A", "119A", "120A", "121A", "122A", "123A",
                    "124A", "125A", "126A", "127A", "128A", "129A", "130A", "130B", "131A",
                    "132A", "133A", "134A", "135A", "136A", "136B", "137A", "137B", "138A",
                    "139A", "140A", "141A", "142A", "143A", "143B", "143C", "143D", "143E",
                    "143F", "143G", "144A", "144B", "144C", "144D", "144E", "144F", "144G",
                    "144H", "144I", "144J", "144K", "144L", "144M", "144N", "144O", "144P",
                    "144Q", "144R", "144S", "144T", "144U", "144V", "144W", "144X", "144Y")

    def __init__(self, features):
        self.features = features

    def _get_wals_template(self):
        wals_url = 'http://wals.info/feature/1A.tab'
        df = pandas.read_csv(wals_url, delimiter='\t', skiprows=7)
        df = df.drop('value', 1)
        df = df.drop('description', 1)
        df = df.rename(columns={'name': 'language'})
        return df

    def _get_wals_data(self, feature):
        wals_url = 'http://wals.info/feature/{}.tab'.format(feature)
        try:
            df_feature = pandas.read_csv(wals_url, delimiter='\t', skiprows=7)
        except:
            print('(Wals) Warning: cannot read Wals feature ' + feature)
        else:
            return df_feature[['wals code','description']]

    def _get_citation(self, feature):
        wals_url = 'http://wals.info/feature/{}.tab'.format(feature)
        wals_page = ur.urlopen(wals_url)
        _citation = 'Citation for feature {}:\n{}\n'
        citation = _citation.format(feature, '\n'.join(wals_page.read().decode('utf-8').split('\n')[:5]))
        return citation

    def get_df(self):
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
        df = self.get_df()

        js = {}
        for header in list(df):
            if not header == 'latitude' and not header == 'longitude' and not header == 'area':
                js[header] = list(df[header])

        coordinates = list(zip(list(df[df._1A == 'Large'].latitude), list(df[df._1A == 'Large'].longitude)))
        js['coordinates'] = coordinates
        return js

#print(Wals('1a').get_json())


