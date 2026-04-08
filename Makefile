PYTHON ?= python3

.PHONY: build test run-sorox run-vossk serve lint

build:
	$(PYTHON) setup.py build_ext --inplace

test:
	$(PYTHON) -m unittest discover -s tests -v

run-sorox:
	PYTHONPATH=src $(PYTHON) -m lumen_veil.cli run --scenario scenarios/sorox_unsealed_arrival.json --steps 6 --pretty

run-vossk:
	PYTHONPATH=src $(PYTHON) -m lumen_veil.cli run --scenario scenarios/vossk_minor_intrusion.json --steps 8 --pretty

serve:
	PYTHONPATH=src $(PYTHON) -m lumen_veil.cli serve --host 127.0.0.1 --port 8787

lint:
	$(PYTHON) -m compileall src tests
