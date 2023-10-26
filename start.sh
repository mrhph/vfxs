#!/bin/bash

export PYTHONPATH="`pwd`/src:`pwd`/lib"
export LIB_LIBRARY_PATH="`pwd`/lib"
poetry run uvicorn vfxs.asgi:app --host 0.0.0.0 --port 8888
