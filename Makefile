doc:
	$(MAKE) -C docs html

test:
	nosetests tests

.PHONY: doc
