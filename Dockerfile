# --- Stage 1: Build dependencies ---
FROM python:3.13-slim AS builder

ARG DEV=false

RUN apt-get update && apt-get install -y \
	libpq-dev \
	gcc \
	python3-dev \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-dev.txt ./

RUN if [ "$DEV" = "true" ] ; then \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements-dev.txt; \
else \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt; \
fi

# --- Stage 2: Final runtime image ---
FROM python:3.13-slim

RUN apt-get update && apt-get install -y libpq5 fonts-dejavu-core && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

RUN pip install --no-cache-dir /wheels/*

COPY . .

EXPOSE 8000