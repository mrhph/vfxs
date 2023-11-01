#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import loguru
import sys
from vfxs.config import LOG_DIR


LOGGER = loguru.logger
# LOGGER.add(sys.stdout)
LOGGER.add(LOG_DIR.joinpath('vfxs.log'), rotation='100MB', retention='100 days')


