#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import setuptools
import pydigitalstrom

setuptools.setup(
    name=pydigitalstrom.__title__,
    version=pydigitalstrom.__version__,
    description=pydigitalstrom.__doc__,
    url=pydigitalstrom.__url__,
    author=pydigitalstrom.__author__,
    author_email=pydigitalstrom.__author_email__,
    license=pydigitalstrom.__license__,
    long_description=open('README.md').read(),
    entry_points={
        'console_scripts': ['dsauth=pydigitalstrom.__main__:main']
    },
    packages=['pydigitalstrom'],
    install_requires=['clint>=0.5.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Home Automation',
    ],
)
