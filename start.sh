
export PYTHONPATH="`pwd`/src"
poetry run uvicorn vfxs.asgi:app --host 0.0.0.0 --port 8888
