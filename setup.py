#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

from setuptools import setup, find_packages


setup(
    name="sysprober",
    version="0.1.1",
    description="Probe your Linux host for information about itself",
    author="Jason C. Nucciarone",
    author_email="jason.nucciarone@canonical.com",
    license="Apache-2.0",
    python_requires=">=3.8",
    packages=find_packages(
        where="src",
        include=["sysprober*"],
    ),
    package_dir={"": "src"},
    install_requires=[
        "pydantic",
    ],
    keywords=[
        "system-administration",
        "automation",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
