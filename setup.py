#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

root = os.path.abspath(os.path.dirname(__file__))

version = __import__('elevator').__version__

with open(os.path.join(root, 'README.md')) as f:
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
        'Development Status :: 0.3d',
        'Environment :: Unix-like Systems',
        'Programming Language :: Python',
        'Operating System :: Unix-like',
    ],
    keywords='elevator leveldb database key-value',

    packages=[
        'elevator',
        'elevator.utils',
    ],
    package_dir={'': '.'},
    zip_safe=False,

    # Setting up executable/main functions links
    entry_points={
        'console_scripts': [
            'elevator = elevator.server:main',
        ]
    },
)
