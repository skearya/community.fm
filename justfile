pre: format check

format: format-server format-web

check: check-server check-web

format-server:
    uv run ruff format

check-server:
    uv run ty check
    uv run ruff check

[working-directory('web')]
format-web:
    npm run format

[working-directory('web')]
check-web:
    npm run check
    npm run lint
