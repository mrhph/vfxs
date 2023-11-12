#!/bin/bash

export PYTHONPATH="`pwd`/src:`pwd`/lib"
export VFX_LOG_DIR="`pwd`/logs"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:`pwd`/lib"
poetry run uvicorn vfxs.asgi:app --host 0.0.0.0 --port 8888
