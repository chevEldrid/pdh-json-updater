test:
	pytest -v tests/

lint:
	pylint pdh_json_updater/ tests/

typing:
	mypy pdh_json_updater/ tests/ --ignore-missing-imports --no-strict-optional

all: test lint typing  ## recommended usage: `make all -k`
