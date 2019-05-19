from setuptools import setup
from lingtypology import __version__

setup(
    name='lingtypology',
    version=__version__,
    description='A tool for linguistic typology.',
    url='https://github.com/OneAdder/lingtypology',
    author='Michael Voronov',
    author_email='mikivo@list.ru',
    license='GPLv3',
    packages=['lingtypology'],
    python_requires='>=3.5',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
          'folium',
          'branca',
          'jinja2',
          'pandas',
          'pyglottolog',
          'colour',
          'matplotlib',
    ],
    extras_require={
        'test': [
            'pytest>=3.6',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Text Processing :: Linguistic',
    ],
) 
