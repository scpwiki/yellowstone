#!/bin/sh

# entrypoint script meant for use by Docker

yes | yoyo apply
exec python -m yellowstone /app/config.toml
