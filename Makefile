test:
	poetry run pytest -v tests/

lint:
	poetry run pylint pdh_json_updater/ tests/

type:
	poetry run mypy pdh_json_updater/ tests/ --ignore-missing-imports --no-strict-optional

all: test lint type  # recommended usage: `make all -k`
