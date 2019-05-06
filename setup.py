from setuptools import setup

setup(
    name='lingtypology',
    version='0.3',
    description='A linguistic tool for interactive mapping.',
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
    ],
    extras_require={
        'test': [
            'pytest>=3.6',
            'pytest-cov',
            'coverage>=4.2',
        ],
    },
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
) 
