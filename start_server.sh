#!/bin/bash

export PYTHONPATH="`pwd`/src:`pwd`/lib"
export VFX_LOG_DIR="`pwd`/logs"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:`pwd`/lib"
poetry run gunicorn -c deploy/gunicorn.conf.py vfxs.asgi:app
