# Webhooked

Webhooked is a simple, lightweight, and easily-hostable request catcher service for viewing HTTP API requests.

Y'know, just like [webhook.site](https://webhook.site/), [Beeceptor](https://beeceptor.com/),
or [RequestBin](https://requestbin.com/), but with a bit more functionality.

It comes with a simple web UI to view all the `Hook`s you've created, along with the `Webhook`s that were sent to the
hook (or, hooked on :')

## Hosting

You can build and run the docker image connecting it to a PostgreSQL database, which is the only dependency.

## Development

### Prerequisites

1. Docker
2. [uv](https://github.com/astral-sh/uv)

### Set Up

1. `cp .env.example .env` to create an `.env` file
2. Start dependencies with `docker compose up -d`
3. Run the app with `uv run fastapi dev app/main.py`
