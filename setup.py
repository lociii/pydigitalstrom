#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
from setuptools import setup, find_packages
import pydigitalstrom


def requirements():
    try:
        return open(
            os.path.join(os.path.dirname(__file__), "requirements.txt")
        ).readlines()
    except IOError:
        return []


def long_description():
    try:
        return open(os.path.join(os.path.dirname(__file__), "README.md")).read()
    except IOError:
        return ""


def changelog():
    try:
        return open(os.path.join(os.path.dirname(__file__), "CHANGELOG.md")).read()
    except IOError:
        return ""


setup(
    name=pydigitalstrom.__title__,
    version=pydigitalstrom.__version__,
    description=pydigitalstrom.__doc__,
    url=pydigitalstrom.__url__,
    author=pydigitalstrom.__author__,
    author_email=pydigitalstrom.__author_email__,
    license=pydigitalstrom.__license__,
    long_description=long_description() + "\n\n" + changelog(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements(),
    keywords=["digitalstrom", "dss", "ds"],
    python_requires=">=3.7.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation",
    ],
)
