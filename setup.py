#!/usr/bin/env python2
from setuptools import setup, find_packages
import os.path

here = os.path.dirname(os.path.abspath(__file__))
about = {}
with open(os.path.join(here, 'omxplayer', '__version__.py'), 'r') as f:
    exec(f.read(), about)

with open(os.path.join(here, 'README.rst'), 'r') as f:
    long_description = f.read()

lib_deps = [
    'dbus-python',
    'evento',
    'decorator',
    'pathlib2',
],

test_deps = [
    'mock',
    'pytest',
    'pytest-cov',
    'nose',
    'parameterized',
]

doc_deps = [
    'Sphinx',
    'alabaster',
    'pygments',
]


setup(
    name='omxplayer-wrapper',

    author=about['__author__'],
    author_email=about['__author_email__'],
    url='https://github.com/willprice/python-omxplayer-wrapper',

    version=about['__version__'],

    description=about['__description__'],
    long_description=long_description,

    license=about['__license__'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Topic :: Multimedia :: Video',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords=' '.join(['omxplayer',
                       'pi',
                       'raspberry',
                       'raspberrypi',
                       'raspberry_pi',
                       'library',
                       'video',
                       'media']),

    packages=find_packages(exclude=['*test*']),
    install_requires=lib_deps,
    test_requires=test_deps,
    extras_require={
        'test': test_deps,
        'docs': doc_deps
    }
)
