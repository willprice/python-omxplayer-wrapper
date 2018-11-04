PYTHON2:=python2
PYTHON3:=python3

.PHONY: init
init:
	pip install ".[test,docs]" -e .

.PHONY: test
test:
	pytest tests/unit --cov-branch --cov=omxplayer

.PHONY: test
test-all:
	tox

.PHONY: dist
dist:
	$(PYTHON3) setup.py sdist
	$(PYTHON3) setup.py bdist_wheel --universal

dist-upload: clean dist
	twine upload dist/*

.PHONY: doc
doc:
	$(MAKE) -C docs html

.PHONY: doc-serve
doc-serve: doc
	cd docs/build/html && $(PYTHON3) -m http.server

clean:
	rm -rf dist build $(shell find . -iname '*.egg-info')
