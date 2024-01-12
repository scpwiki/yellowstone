## bzhr &mdash; Comprehensive Backups for Wikidot

A new comprehensive backup system for Wikidot, maintained by the SCP-EN Technical Team and contributors.

This program is written for Python 3.11 or later. You will need a Wikidot API key, which you can get if you have a [Pro Plan](https://www.wikidot.com/plans).

### Setup

Create a Python virtual environment, and then install this project's dependencies:

```
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

Then when doing development, install the development dependencies and then run linting to ensure things are in order:

```
$ pip install -r requirements.dev.txt
$ ruff check bzhr
$ ruff format bzhr
$ mypy bzhr
```

Then, to run a local instance, create a `config.toml` file (see `config.example.toml` as an example) and run:

```
$ python -m bzhr config.toml
```

If you are packaging for a production deployment, the easiest method is to build a Docker image and ship that:

```
$ docker build -t scpwiki/bzhr:latest .
```

### License and Naming

This software is available for use under the terms of the GNU General Public License v2 only.

The project is named for the Bright/Zartion Hominid Replicators (BZHR) from [SCP-2000](https://scpwiki.com/scp-2000), an anomaly meant to be able to "reset" the world in case of a significant K-class event. The BZHR system is the heart of SCP-2000, able to mass-manufacture humans to repopulate Earth.
