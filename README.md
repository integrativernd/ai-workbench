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

## Folder Structure

```
.
├── Procfile
├── Procfile.windows
├── README.md
├── app.json
├── bin
│   └── deploy
├── channels
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_message.py
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── config
│   ├── SYSTEM_PROMPT.txt
│   ├── __init__.py
│   ├── __pycache__
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── discord_server
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── worker.py
├── discord_server.py
├── llm
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── analyze.py
│   ├── anthropic_integration.py
│   ├── apps.py
│   ├── migrations
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── models.py
│   ├── respond.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── fixtures
│   │   │   ├── basic_message_test.pickle
│   │   │   ├── performance_test.pickle
│   │   │   └── serper_result.json
│   │   └── test_anthropic_integration.py
│   └── views.py
├── manage.py
├── requirements.txt
├── runtime.txt
├── tools
│   ├── __init__.py
│   ├── __pycache__
│   ├── admin.py
│   ├── apps.py
│   ├── browse.py
│   ├── github_create_pr.py
│   ├── github_example.py
│   ├── migrations
│   │   ├── __init__.py
│   │   └── __pycache__
│   ├── models.py
│   ├── search.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── fixtures
│   │   │   ├── capital_of_france.pickle
│   │   │   └── example_com_content.json
│   │   ├── test_browse.py
│   │   └── test_search.py
│   ├── update_file.py
│   └── views.py
└── web
    ├── __init__.py
    ├── __pycache__
    ├── admin.py
    ├── apps.py
    ├── migrations
    │   ├── 0001_initial.py
    │   ├── __init__.py
    │   └── __pycache__
    ├── models.py
    ├── static
    ├── templates
    │   ├── base.html
    │   ├── db.html
    │   └── index.html
    ├── tests.py
    └── views.py
```

## Getting Started

python3 -m venv --upgrade-deps .venv

heroku local --port 5001

### Create a Super User

```bash
python manage.py createsuperuser
```

## Heroku App Dependencies

heroku buildpacks:add -i 1 heroku-community/chrome-for-testing
