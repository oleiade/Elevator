#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup
import os
import elevator


setup(
    name = "Elevator",
    version = "0.0.1",
    license = "BSD",

    description = "Minimalistic database engine based on levelDB. Allows async, multithreaded and/or remote acces to a leveldb backend.",

    author = "Oleiade",
    author_email = "tcrevon@gmail.com",
    url = "http://github.com/oleiade/Elevator",

    classifiers = [
        'Development Status :: 0.0.1 - Early Alpha',
        'Environment :: Unix-like Systems',
        'Programming Language :: Python',
        'Operating System :: Unix-like',
    ],
    keywords = "elevator leveldb database key-value",

    packages = [
        'elevator',
        'elevator.utils',
        ],
    package_dir = {'': '.'},

    install_requires = [
        'pyzmq>=2.1.11',
        ],

    # Setting up executable/main functions links
    entry_points = {
        'console_scripts': [
            'elevator = elevator.server:run',
        ]
    },

)
