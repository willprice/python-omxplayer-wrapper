from setuptools import setup, find_packages

setup(
    name='omxplayer-wrapper',

    author='Will Price',
    author_email='will.price94+dev@gmail.com',
    url='https://github.com/willprice/python-omxplayer-wrapper',

    version='0.0.2',

    description='Control OMXPlayer on the Raspberry Pi',
    long_description='Control OMXPlayer on the Raspberry Pi through DBus',

    license='LGPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Topic :: Multimedia :: Video',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='omxplayer pi raspberry raspberrypi raspberry_pi library',

    packages=find_packages(exclude=['*tests']),
    # Depends on dbus-python which is only shipped via package managers or as a
    # source dist (incompatible with distutils
    install_requires=[
        'decorator',
    ],
    extras_require={
        'test': [
            'nose',
            'mock',
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
