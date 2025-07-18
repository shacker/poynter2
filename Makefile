.venv/bin/python3.13:
	python3.13 -m venv --prompt $(shell basename $(shell pwd)) .venv
	.venv/bin/pip install -U setuptools wheel pip

requirements.txt: requirements/base.in
	.venv/bin/pip-compile --generate-hashes --output-file $@ requirements/base.in

requirements/dev.txt: requirements.txt requirements/dev.in
	.venv/bin/pip-compile --generate-hashes --output-file $@ requirements/dev.in

.PHONY: install
install: .venv/bin/python3.13
	.venv/bin/pip install -r requirements.txt -r requirements/dev.txt
	.venv/bin/pip install -e .

.PHONY: dev_refresh
dev_refresh: install
	./manage.py migrate
	.venv/bin/pre-commit install
