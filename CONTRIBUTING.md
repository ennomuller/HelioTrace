# Contributing

## Dev environment

Clone and install all dependencies (core + dev tools):

    git clone https://github.com/ennomuller/HelioTrace.git
    cd HelioTrace
    uv sync        # installs core + [dependency-groups] dev automatically

## Running quality checks

    uv run pytest                 # test suite
    uv run ruff check .           # lint
    uv run ruff format .          # format
    uv run pyright src/           # type-check

## Pre-commit hooks (recommended)

    uv run pre-commit install     # wire hooks into .git/hooks
    uv run pre-commit autoupdate  # bump all hook revisions to latest

Hooks run Ruff (lint + format) automatically on every commit.
