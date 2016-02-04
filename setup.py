# Copyright (c) 2015, Adrian Stoewer (adrian.stoewer@rz.ifi.lmu.de)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the project.

import re
from setuptools import setup, find_packages


with open("README.md") as f:
    description_text = f.read()

with open("LICENSE.txt") as f:
    license_text = f.read()

with open("odml2/info.py") as f:
    info = f.read()

VERSION = re.search(r"VERSION\s*=\s*'([^']*)'", info).group(1)
AUTHORS = re.search(r"AUTHORS\s*=\s*'([^']*)'", info).group(1)
CONTACT = re.search(r"CONTACT\s*=\s*'([^']*)'", info).group(1)
DESCRIPTION = re.search(r"DESCRIPTION\s*=\s*'([^']*)'", info).group(1)
LONG_DESC = re.search(r"LONG_DESC\s*=\s*'([^']*)'", info).group(1)
HOMEPAGE = re.search(r"HOMEPAGE\s*=\s*'([^']*)'", info).group(1)
PACKAGE = re.search(r"PACKAGE\s*=\s*'([^']*)'", info).group(1)
LICENSE = re.search(r"LICENSE\s*=\s*'([^']*)'", info).group(1)

setup(
    name=PACKAGE,
    url=HOMEPAGE,
    author=AUTHORS,
    version=VERSION,
    author_email=CONTACT,
    description=DESCRIPTION,
    long_description=LONG_DESC,
    license=LICENSE,

    packages=find_packages(exclude=("test", )),

    install_requires=(
        "setuptools",
        "six",
        "future",
        "sortedcontainers",
        "PyYAML>=3.10"
    ),
    tests_require=(
        "nose"
    ),
    test_suite='nose.collector',

    classifiers=(
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ),

    package_data={PACKAGE: [license_text, description_text]},
    include_package_data=True,
    zip_safe=True
)
