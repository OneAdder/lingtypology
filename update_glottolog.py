import os

def download_glottolog(git_path='git'):
    yes = input('Are you sure you want to download the latest copy of Glottolog DB? [Y/n]')
    
    if yes == 'y' or yes == '':
        if not 'glottolog' in os.listdir():
            print('Downloading data...')
            os.system(git_path + " clone https://github.com/clld/glottolog")
        else:
            print('It seems that the database is already downloaded')
    else:
        print('Aborted')

def update_data(pyglottolog_path='glottolog'):
    print('Updating the data...')
    os.system(pyglottolog_path + ' --repos=glottolog languoids')
    print('Moving data to your installation of lingtypology')
    table_name = [path for path in os.listdir() if path.startswith('glottolog-languoids') and path.endswith('.csv')][0]
    os.system('cp ' + table_name + ' ' + os.path.join(os.getcwd(), table_name))
    print('Data successfully moved')

def update_glottolog(git_path='git', pyglottolog_path='glottolog'):
    download_glottolog(git_path=git_path)
    update_data(pyglottolog_path=pyglottolog_path)
