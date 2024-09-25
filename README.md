# AI Workbench

The AI Workbench is a framework for building semi-autonomous AI agents that can be used to automate tasks in a variety of domains. The AI Workbench is designed to be modular and extensible, allowing developers to easily add new capabilities to their agents.

## Overview

The AI Workbench is built on top of the [Django](https://www.djangoproject.com/) web framework and uses [rq](https://python-rq.org/) for task scheduling. The AI Workbench provides a web-based interface for managing agents, tasks, and datasets, as well as a REST API for interacting with agents programmatically.

Django is used for managing the Database and admin interface. rq is used for managing the task queue. The AI Workbench provides a chat-base interface for managing agents, tasks, and datasets, as well as a REST API for interacting with agents programmatically.

## System Requirements for Development

- Python 3.6+
- MacOS or Linux
- Redis
- Heroku CLI

## Software Architecture

Core modules are implemented as Django apps. Each app is responsible for a specific aspect of the system, such as managing agents, tasks, or datasets. The core modules are designed to be extensible, allowing developers to easily add new capabilities to their agents.

## Getting Started

python3 -m venv --upgrade-deps .venv

heroku local --port 5001

### Create a Super User

```bash
python manage.py createsuperuser
```

## Heroku Apps

heroku buildpacks:add -i 1 heroku-community/chrome-for-testing
