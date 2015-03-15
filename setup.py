from setuptools import setup

setup(
    name='omxplayer-wrapper',

    author='Will Price',
    author_email='will.price94+py@gmail.com',

    version='0.1',

    description='Control OMXPlayer on the Raspberry Pi',
    long_description='Control OMXPlayer on the Raspberry Pi through DBus',

    license='LGPL',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Video',
        'Programming Language :: Python :: 2'
    ],

    keywords='omxplayer, raspberry_pi, library',

    packages=['omxplayer'],
    install_requires=[],
)
