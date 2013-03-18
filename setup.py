#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup

root = os.path.abspath(os.path.dirname(__file__))

version = __import__('elevator').__version__

with open(os.path.join(root, 'README.rst')) as f:
    README = f.read()

with open(os.path.join(root, 'CHANGES.rst')) as f:
    CHANGES = f.read()

setup(
    name='Elevator',
    version=version,
    license='MIT',

    description='On disk key/value store based on levelDB backend',
   long_description=README + '\n\n' + CHANGES,

    author='Oleiade',
    author_email='tcrevon@gmail.com',
    url='http://github.com/oleiade/Elevator',

    classifiers=[
        'Topic :: Database :: Database Engines/Servers',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
    ],
    keywords='elevator leveldb database key-value',

    packages=[
        'elevator',
        'elevator.backend',
        'elevator.utils',
        'elevator.helpers',

        'elevator_cli',
    ],
    package_dir={'': '.'},
    include_package_data=False,

    zip_safe=True,
    install_requires=[
        'lz4',
        'python-daemon==1.5.5',
        'msgpack-python',
        'pyzmq==13.0.0',
        'unittest2',
        'ujson',
        'procname',
        'clint',
        'plyvel',
        'fabric',
    ],

    # Setting up executable/main functions links
    entry_points={
        'console_scripts': [
            'elevator = elevator.server:main',
            'elevator-cli = elevator_cli.main:main',
        ]
    },
)
