# syntax=docker/dockerfile:1

FROM python:3.13.11-alpine3.23

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install uv

COPY ./uv.lock /app/uv.lock
COPY ./pyproject.toml /app/pyproject.toml

RUN uv sync --locked --no-dev

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application on the production server.
CMD ["uv", "run", "uvicorn", "--host", "0.0.0.0", "madr.app:app"]
