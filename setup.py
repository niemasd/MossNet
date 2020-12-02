"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
setup(
    name='mossnet',   # Required
    version='0.0.15',  # Required
    description='A Python package for performing network analyses on MOSS results',  # Required
    long_description='',  # Optional
    long_description_content_type='text/plain',  # Optional (see note above)
    url='https://github.com/niemasd/MossNet',  # Optional
    author='Niema Moshiri',  # Optional
    author_email='niemamoshiri@gmail.com',  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='education moss plagiarism coding programming',  # Optional
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    install_requires=[
        'bs4',
        'lxml',
        'networkx',
    ],
    extras_require={  # Optional
        'dev': ['check-manifest'],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/niemasd/MossNet/issues',
        'Source': 'https://github.com/niemasd/MossNet',
    },
)
