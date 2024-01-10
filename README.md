## bzhr &mdash; Comprehensive Backups for Wikidot

A new comprehensive backup system for Wikidot, maintained by the SCP-EN Technical Team.

This program is written for Python 3.11 or later.

### Setup

Create a Python virtual environment, and then install this project's dependencies:

```
$ python -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

If you are packaging for a production deployment, the easiest method is to build a Docker image and ship that:

```
$ docker build -t scpwiki/bzhr:latest .
```

### License and Naming

This software is available for use under the terms of the GNU General Public License v2 Only.

The project is named for the _Bright/Zartion Hominid Replicators (BZHR)_ from [SCP-2000](https://scpwiki.com/scp-2000), an anomaly meant to be able to "reset" humanity in case of a significant K-class event. The BZHR system is the heart of SCP-2000, able to manufacture enough humans to repopulate Earth.
