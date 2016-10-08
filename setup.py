#!/usr/bin/env python2
from setuptools import setup, find_packages

setup(
    name='omxplayer-wrapper',

    author='Will Price',
    author_email='will.price94+dev@gmail.com',
    url='https://github.com/willprice/python-omxplayer-wrapper',

    version='0.1.0',

    description='Control OMXPlayer on the Raspberry Pi',
    long_description='Control OMXPlayer on the Raspberry Pi through DBus',

    license='LGPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Topic :: Multimedia :: Video',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='omxplayer pi raspberry raspberrypi raspberry_pi library video media',

    packages=find_packages(exclude=['*tests']),
    # Depends on dbus-python which is only shipped via package managers or as a
    # source dist (incompatible with distutils
    install_requires=[
        'decorator',
        'evento'
    ],
    extras_require={
        'test': [
            'mock',
            'nose',
            'nose-parameterized',
        ],
        'docs': [
            'Sphinx',
            'sphinxcontrib-napoleon',
            'sphinx-rtd-theme',
            'pygments',
        ]
    }
)
