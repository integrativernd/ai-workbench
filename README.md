# AI Workbench

The AI Workbench is a framework for building semi-autonomous AI agents that can be used to automate tasks in a variety of domains. The AI Workbench is designed to be modular and extensible, allowing developers to easily add new capabilities to their agents.

## Overview

The AI Workbench is built on top of the [Django](https://www.djangoproject.com/) web framework and uses [rq](https://python-rq.org/) for task scheduling. The AI Workbench provides a web-based interface for managing agents, tasks, and datasets, as well as a REST API for interacting with agents programmatically.

## Getting Started

python3 -m venv --upgrade-deps .venv

heroku local --port 5001

### Create a Super User

```bash
python manage.py createsuperuser
```
