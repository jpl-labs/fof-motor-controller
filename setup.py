#!/usr/bin/env python

from distutils.core import setup

setup(
    name='MotorController',
    version='1.0',
    description='Python script to control the fan motors in the Fans of Fury game.',
    license='MIT',
    url='https://github.com/omni-resources/fof-motor-controller',
    packages=['motor-controller'],
    entry_points={
        'console_scripts': [
            'motor-controller = motor-controller.__main__:main'
        ]
    }
)
