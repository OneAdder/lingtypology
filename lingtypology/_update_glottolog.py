import subprocess
import os

MODULE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

def download_glottolog(git_path='git'):
    """Downloads Glottolog data into current directory.

    git_path: str, default 'git'
        Path to particular git binary.
    """
    yes = input('Are you sure you want to download the latest copy of Glottolog DB? It will require 500 MiB (temporarily). [Y/n]')
    
    if yes in ('y', 'yes') or yes == '':
        if not 'glottolog' in os.listdir():
            print('Downloading data. This can take some time...')
            subprocess.run([git_path, 'clone', 'https://github.com/clld/glottolog'])
        else:
            update = input('It seems that the database is already downloaded. Update? [Y/n]')
            if update in ('y', 'yes') or update == '':
                print('Downloading data. This can take some time...')
                subprocess.run(['rm', '-rf', 'glottolog'])
                subprocess.run([git_path, 'clone', 'https://github.com/clld/glottolog', 'glottolog'])
            else:
                print('Aborted')
    else:
        print('Aborted')

def update_data(pyglottolog_path='glottolog'):
    """Runs glottolog app and copies data to the installation directory.

    pyglottolog_path: str, default 'glottolog'
        Path to particular glottolog binary.
    """
    print('Updating the data...')
    subprocess.run([pyglottolog_path, '--repos=glottolog', 'languoids'])
    subprocess.run(['rm', '-rf', 'glottolog'])
    print('Moving data to your installation of lingtypology')
    table_name = [path for path in os.listdir() if path.startswith('glottolog-languoids') and path.endswith('.csv')][0]
    table_data = [path for path in os.listdir() if path.startswith('glottolog-languoids') and path.endswith('.json')][0]
    subprocess.run(['mv', table_name, os.path.join(MODULE_DIRECTORY, table_name)])
    subprocess.run(['mv', table_data, os.path.join(MODULE_DIRECTORY, table_data)])
    old_table_name = [path for path in os.listdir(MODULE_DIRECTORY) if path.startswith('glottolog-languoids') and path.endswith('.csv')][0]
    old_table_data = [path for path in os.listdir(MODULE_DIRECTORY) if path.startswith('glottolog-languoids') and path.endswith('.json')][0]
    subprocess.run(['rm', os.path.join(MODULE_DIRECTORY, old_table_name), os.path.join(MODULE_DIRECTORY, old_table_data)])
    print('Data successfully moved')

def update_glottolog(git_path='git', pyglottolog_path='glottolog'):
    """Update Glottolog data.

    This function:
        1) downloads the latest copy of Glottolog data;
        2) runs glottolog app (from pyglottolog);
        3) copies the data from current directory to the package installation directory.

    Parameters
    ----------
    git_path: str, default 'git'
        Path to particular git binary (e.g. '/usr/bin/git').
        Might be useful if you are using Windows.
    pyglottolog_path: str, default 'glottolog'
        Path to particular glottolog binary.
        Might be useful if you are using Windows.
    """
    download_glottolog(git_path=git_path)
    update_data(pyglottolog_path=pyglottolog_path)
