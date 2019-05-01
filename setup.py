from setuptools import setup

setup(
    name='lingtypology',
    version='0.1',
    description='A linguistic tool for interactive mapping.',
    url='https://github.com/OneAdder/lingtypology',
    author='Michael Voronov',
    author_email='mikivo@list.ru',
    license='GPLv3',
    packages=['lingtypology'],
    zip_safe=False,
    install_requires=[
          'folium',
          'branca',
          'jinja2',
          'pandas',
          'pyglottolog',
    ],
    include_package_data=True,
)  
