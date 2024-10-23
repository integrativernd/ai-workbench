# AI Workbench

The AI Workbench is a framework for building semi-autonomous AI agents that can be used to automate tasks in a variety of domains. The AI Workbench is designed to be modular and extensible, allowing developers to easily add new capabilities to their agents.

## Introduction

The AI Workbench is built on top of the [Django](https://www.djangoproject.com/) web framework and uses Temporal for task scheduling. The AI Workbench provides a web-based interface for managing agents, tasks, and datasets, as well as a REST API for interacting with agents programmatically.

Django is used for managing the Database and admin interface. Temporal is used for managing running workflows in the background. The AI Workbench provides a chat-base interface for managing agents, tasks, and datasets, as well as a REST API for interacting with agents programmatically.

## System Requirements

- Python 3.6+
- MacOS or Linux
- Redis
- Postgresql

## Software Architecture

Core modules are implemented as Django apps. Each app is responsible for a specific aspect of the system, such as managing agents, tasks, or datasets. The core modules are designed to be extensible, allowing developers to easily add new capabilities to their agents.

## Getting Started

Create a virtual environment

```Shell
python3 -m venv --upgrade-deps .venv
```

Install python dependencies

```Shell
pip install -r requirements.txt
```

heroku local --port 5001

### Create a Super User

```bash
python manage.py createsuperuser
```

## Heroku App Dependencies

heroku buildpacks:add -i 1 heroku-community/chrome-for-testing

## Testing

```
python manage.py test
```
