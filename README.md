## Yellowstone &mdash; Comprehensive Backups for Wikidot

_(Work in progress)_

A new comprehensive backup system for Wikidot, maintained by the SCP-EN Technical Team and contributors.

This program is written for Python 3.11 or later. You will need a Wikidot API key, which you can get if you have a [Pro Plan](https://www.wikidot.com/plans).

### Configuration

The `.env` file is sourced by the process to pull in secrets. Look at `.env.example` for the expected structure of this file. These secrets can also be set in the environment directly.

Within `yoyo.ini`, override the database URL with the value of `$POSTGRES_DATABASE_URL`.

### Setup

Create a Python virtual environment, and then install this project's dependencies:

```bash
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

Then when doing development, install the development dependencies and then run linting to ensure things are in order:

```bash
$ pip install -r requirements.dev.txt
$ ruff check -n yellowstone test  # -n here and below means --no-cache
$ ruff format -n yellowstone test
$ mypy yellowstone
```

Then, to run a local instance, create a `config.toml` file (see `config.example.toml` as an example) and run:

```bash
$ python -m yellowstone config.toml
```

If you are packaging for a production deployment, the easiest method is to build a Docker image and ship that:

```bash
$ docker build -t scpwiki/yellowstone:latest .
```

### Testing

You can run the unit test suite:

```bash
$ python -m unittest
```

It is also possible to run specific test files if you wish:

```bash
$ python -m unittest test.test_scraper
```

### License and Naming

This software is available for use under the terms of the GNU General Public License v2 only.

The project is named for [SCP-2000](https://scpwiki.com/scp-2000), an anomaly meant to be able to "reset" the world in case of a significant K-class event. This anomaly is kept underground in Yellowstone National Park, thus the name.
