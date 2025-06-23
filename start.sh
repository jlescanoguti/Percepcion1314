#!/bin/sh
echo "DEBUG: PORT is '$PORT'"
env
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}