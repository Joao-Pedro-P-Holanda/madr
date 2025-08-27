# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.13.5
FROM python:${PYTHON_VERSION}-alpine AS base

ENV POETRY_VIRTUALENVS_CREATE=false
# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install poetry

# Copy the source code into the container.
COPY . .

# upgrades the database to the head migration
RUN poetry install --no-interaction --no-ansi --without dev

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application on the production server.
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "madr.app:app"]
