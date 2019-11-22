"""Setuptools script for FuzzyBoa."""

from setuptools import setup

setup(
    name="com.github.aidanPB.fuzzyboa",
    version="0.1",
    author='Aidan Pitt-Brooke',
    author_email='f.sylvestris@gmail.com',
    description='A FuzzBall-like MUCK server implemented in Python',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)',
        'License :: OSI Approved :: ISC License (ISCL)',
        ],
    python_requires='~=3.6',
    install_requires=[
        'telnetlib3~=1.0.2',
        ],
    packages=['fuzzyboa'],
    entry_points={},
    )
