.PHONY: check
check: test

.PHONY: test
test:
	nosetests --with-coverage \
              --cover-erase \
              --cover-xml \
              --cover-html \
              --cover-branches \
              --cover-package=omxplayer \
              tests

.PHONY: doc
doc:
	$(MAKE) -C docs html
