#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# JSM product code
#
# (C) Copyright 2017 Juxt SmartMandate Pvt Ltd
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#

"""
Small command line application to find the Py4J directory. This is required so
both the Python and bash sources in CliNER can execute this.
"""

import os.path as op
from cliner.features_dir.read_config import enabled_modules


def get_py4j_dir():
    modules = enabled_modules()
    return op.dirname(modules.get('PY4J', ''))

if __name__ == '__main__':
    print(get_py4j_dir())
