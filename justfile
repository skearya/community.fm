format:
    uv run ruff format

check:
    uv run ty check
    uv run ruff check

publish: format check
    docker build -t ghcr.io/skearya/radio:latest -f packages/server/Dockerfile .
    docker push ghcr.io/skearya/radio:latest
