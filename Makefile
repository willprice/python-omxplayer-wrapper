PYTHON2:=python2
PYTHON3:=python3

.PHONY: check
check: test

.PHONY: test
test:
	tox

.PHONY: dist
dist: test
	$(PYTHON3) setup.py bdist_wheel --universal

dist-upload: clean-dist dist
	twine upload dist/*

clean-dist:
	rm -rf build
	rm -rf dist

.PHONY: doc
doc:
	$(MAKE) -C docs html
