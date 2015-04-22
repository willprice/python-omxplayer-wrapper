doc:
	$(MAKE) -C doc html

test:
	nosetests tests

.PHONY: doc
