.PHONY: check
check: test

.PHONY: test
test:
	tox

.PHONY: doc
doc:
	$(MAKE) -C docs html
