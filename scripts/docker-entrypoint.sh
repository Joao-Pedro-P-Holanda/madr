#!/bin/sh
uv run alembic upgrade head
uv run uvicorn --host 0.0.0.0 madr.app:app
