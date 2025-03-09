# aioamqp-stubs
Stubs for [aioamqp](https://github.com/Polyconseil/aioamqp).

## Usage
Just install and that's all!
```bash
pip install aioamqp-stubs
```

## Development
### Tests
1. Install [tox](https://github.com/tox-dev/tox).
2. Run tox
```bash
tox -p
```

### pre-commit
There's [pre-commit](https://github.com/pre-commit/pre-commit) configured.
```bash
poetry install
poetry run pre-commit install
```

### Build
Use [poetry](https://github.com/python-poetry/poetry) for building.
```bash
poetry build
poetry publish
```
