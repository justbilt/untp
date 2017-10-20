#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'untp',
    version = '1.1.2',
    description = 'A command line tool to split TexturePacker published files.',
    url = 'https://github.com/justbilt/untp',
    author = 'justbilt',
    author_email = 'wangbilt@gmail.com',
    license = 'MIT License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],    
    keywords = 'untp texturepacker cocos',
    install_requires = [
        'Pillow',
        'parse'
    ],
    packages = find_packages("src"),
    package_dir = {'':'src'},
    entry_points = {
        'console_scripts': [
            'untp = untp.untp:main',
        ],
    }
)