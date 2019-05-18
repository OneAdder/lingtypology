import pandas
import os
import lingtypology
import numpy as np
import matplotlib.pyplot as plt
from lingtypology.db_apis import Phoible
from scipy.stats import linregress, chi2_contingency

def fwrite(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)

def count_stats(subset, feature):
    p = Phoible(subset=subset, aggregated=False)
    p.show_citation = False
    data = p.get_df()
    amount_with_feature = data[data[feature] == '+'].groupby('Glottocode').size()
    
    languages = [lingtypology.glottolog.get_by_glot_id(glot_id) for glot_id in amount_with_feature.index]
    with_feature = pandas.DataFrame({
        'language': languages,
        feature: amount_with_feature,
        'elevation': lingtypology.get_elevations(languages),
    })
    with_feature = with_feature[with_feature.elevation != '']
    if with_feature.empty:
        print('No data: ' + subset)
        return

    #Зависит ли количество абруптивных/имплозивных в языках, где они суть, от высоты
    regression_no_zeros = linregress(
        list(map(int, with_feature[feature])),
        list(map(int, with_feature.elevation))
    )
    
    no_feature = data[~data.Glottocode.isin(list(amount_with_feature.index))]
    no_feature = no_feature.drop_duplicates(subset='Glottocode')
    languages = [lingtypology.glottolog.get_by_glot_id(glot_id) for glot_id in no_feature.Glottocode]
    no_feature = pandas.DataFrame({
        'language': languages,
        feature: 0,
        'elevation': lingtypology.get_elevations(languages),
    })
    no_feature = no_feature[no_feature.elevation != '']
    all_ = pandas.concat((with_feature, no_feature))

    #Зависит ли количество абруптивных/имплозивных во всех яхыках от высоты
    regression_with_zeros = linregress(
        list(map(int, all_[feature])),
        list(map(int, all_.elevation))
    )

    higher = all_[all_.elevation > 1500]
    higher = [len(higher[higher[feature] > 0]), len(higher[higher[feature] == 0])]
    lower = all_[all_.elevation <= 1500]
    lower = [len(lower[lower[feature] > 0]), len(lower[lower[feature] == 0])]
    table = [higher, lower]
    
    #Правда ли, что, если больше 1500 метров, то ты абруптивный/имплозивный?
    chi = chi2_contingency(table)
    
    #Нарисуем все графики и запишем все данные в файлы
    cdir = 'ejectives_implosives_data' + os.path.sep + subset
    if not os.path.exists(cdir):
        os.mkdir(cdir)

    #График регрессия для языков с фичёй
    plt.scatter(with_feature[feature], with_feature.elevation, color='black')
    axes = plt.gca()
    x_vals = np.array(axes.get_xlim())
    y_vals = regression_no_zeros.intercept + regression_no_zeros.slope*x_vals 
    plt.plot(x_vals, y_vals, linewidth=3)
    plt.savefig(cdir + os.path.sep + 'linear_regression_{}_only.png'.format(feature), format='PNG')
    plt.cla()
    plt.clf()
    
    #График регрессии для всех языков по фиче
    plt.scatter(all_[feature], all_.elevation, color='black')
    axes = plt.gca()
    x_vals = np.array(axes.get_xlim())
    y_vals = regression_with_zeros.intercept + regression_with_zeros.slope*x_vals 
    plt.plot(x_vals, y_vals, linewidth=3)
    plt.savefig(cdir + os.path.sep + 'linear_regression_{}_all.png'.format(feature), format='PNG')
    plt.cla()
    plt.clf()
    
    #Результаты подсчёта регрессии
    reg_str = 'Slope:\t{slope}\nIntercept:\t{intercept}\nR_value:\t{rvalue}\nP_value:\t{pvalue}'
    fwrite(
        cdir + os.path.sep + 'linear_regression_{}_only.csv'.format(feature),
        reg_str.format(
            slope = regression_no_zeros.slope,
            intercept = regression_no_zeros.intercept,
            rvalue = regression_no_zeros.rvalue,
            pvalue = regression_no_zeros.pvalue
        )
    )
    fwrite(
        cdir + os.path.sep + 'linear_regression_{}_all.csv'.format(feature),
        reg_str.format(
            slope = regression_with_zeros.slope,
            intercept = regression_with_zeros.intercept,
            rvalue = regression_with_zeros.rvalue,
            pvalue = regression_with_zeros.pvalue
        )
    )
    
    #Результаты хи-квадрата
    fwrite(
        cdir + os.path.sep + 'chi2_{}.csv'.format(feature),
        'chi2:\t{chi2}\nP_value:\t{pvalue}\nDegrees of freedom:\t{dof}\nExpected:\t{ex}'.format(
            chi2 = chi[0],
            pvalue = chi[1],
            dof = chi[2],
            ex = chi[3]
        )
    )
    
    #Чистые данные
    with_feature.to_csv(cdir + os.path.sep + 'with_{}_raw.csv'.format(feature))
    all_.to_csv(cdir + os.path.sep + 'all_{}_raw.csv'.format(feature))
        
    return regression_no_zeros, regression_with_zeros, chi, subset

if __name__ == '__main__':
    features = ['loweredLarynxImplosive', 'raisedLarynxEjective']
    subsets = ['UPSID', 'SPA', 'AA', 'PH', 'GM', 'RA', 'SAPHON']
    results = {}
    if not os.path.exists('ejectives_implosives_data'):
        os.mkdir('ejectives_implosives_data')
    for feature in features:
        processed_subsets = []
        regressions_no_zeros = []
        regressions_with_zeros = []
        chi2s = []
        for subset in subsets:
            r = count_stats(subset, feature)
            if r:
                regressions_no_zeros.append(r[0])
                regressions_with_zeros.append(r[1])
                chi2s.append(r[2])
                processed_subsets.append(r[3])
        plt.close()
        result = pandas.DataFrame({
            'Dataset': processed_subsets,
            'Regression (only with feature)': ['%.015f' % r.pvalue for r in regressions_no_zeros],
            'Regression (all languages)': ['%.015f' % r.pvalue for r in regressions_with_zeros],
            'Chi2 Test': ['%.015f' % c[1] for c in chi2s]
        })
        results[feature] = result
