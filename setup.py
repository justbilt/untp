#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'untp',
    version = '1.0.6',
    keywords = ('untp', 'texturepacker'),
    description = 'A command line tool to split TexturePacker publish file.',
    license = 'MIT License',
    install_requires = [
        'Pillow',
        'parse'
    ],
    url = 'https://github.com/justbilt/untp',
    author = 'justbilt',
    author_email = 'wangbilt@gmail.com',
    packages = find_packages("src"),
    package_dir = {'':'src'},
    entry_points = {
        'console_scripts': [
            'untp = untp.untp:main',
        ],
    }
)