#!/usr/bin/env python

from setuptools import setup

setup(
    name='MotorController',
    version='1.0',
    description='Python script to control the fan motors in the Fans of Fury game.',
    license='MIT',
    url='https://github.com/omni-resources/fof-motor-controller',
    packages=['motor_controller'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'motor-controller = motor_controller.__main__:main'
        ]
    }
)
