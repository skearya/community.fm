# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS builder

# Install git (needed to fetch non-pypi deps)
RUN apk add --no-cache git

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-workspace --package=server

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package=server


# Then, use a final image without uv
FROM python:3.14-alpine AS runner
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Install ffmpeg & deno (needed for yt-dlp), opus (needed for bot streaming)
RUN apk add --no-cache deno ffmpeg opus-dev

# Setup a non-root user
RUN addgroup -g 1000 -S nonroot \
    && adduser -u 1000 -G nonroot -S -D nonroot

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Use the non-root user to run our application
USER nonroot

# Use `/app` as the working directory
WORKDIR /app

# Run the server
CMD ["python", "packages/server/src/main.py"]


FROM runner AS development


FROM node:26-alpine AS web-builder

# Install the project into `/web`
WORKDIR /web

# Install production dependencies
RUN --mount=type=cache,target=/root/.npm,sharing=locked \
    --mount=type=bind,source=web/package-lock.json,target=package-lock.json \
    --mount=type=bind,source=web/package.json,target=package.json \
    --mount=type=bind,source=web/svelte.config.js,target=svelte.config.js \
    npm ci --no-audit --no-fund

# Copy source files
COPY web .

# Build site, files accesible at /web/build
RUN npm run build


FROM runner AS production

# Copy web build
COPY --from=web-builder /web/build /static
