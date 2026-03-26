#!/bin/sh
poetry run alembic upgrade head
poety run uvicorn --host 0.0.0.0 madr.app:app
