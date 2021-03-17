SHELL = /bin/bash

.PHONY: check clean

.DEFAULT_GOAL := showoptions

APP_NAME = retroplay
APP_VERSION := $(shell python3 "./$(APP_NAME).py" --app version --quiet --norun)
APP_DATE := $(shell python3 "./$(APP_NAME).py" --app date --quiet --norun)
APP_AUTHOR := $(shell python3 "./$(APP_NAME).py" --app author --quiet --norun)

DISTDIR = ./dist
PYTHON_PACKAGE_FILENAME = $(APP_NAME)-$(APP_VERSION)-Python.tar.gz
BINARY_PACKAGE_FILENAME = $(APP_NAME)-$(APP_VERSION)-Linux-64Bit.tar.gz

INSTALLCMD = /usr/bin/install
INSTALLDIR_BIN = /usr/local/bin
INSTALLDIR_DOC = /usr/local/doc
INSTALLDIR_MAN = /usr/local/man/man6

all: check clean py bin

install: install.sh
	cd "./$(APP_NAME)" && sudo "./install.sh"

uninstall: uninstall.sh
	cd "./$(APP_NAME)" && sudo "./uninstall.sh"

py: packpy
	mv "$(PYTHON_PACKAGE_FILENAME)" "$(DISTDIR)/"

bin: packbin
	mv $(BINARY_PACKAGE_FILENAME) "$(DISTDIR)/"

doc: builddoc

builddoc:
	pandoc "./README.md" -s -t html -o "./README.html"
	-rm -f "./$(APP_NAME).6"
	pandoc "$(APP_NAME).6.md" -s -t man -o "$(APP_NAME).6"
	sed -i "s/%APP_DATE%/$(APP_DATE)/" "$(APP_NAME).6"
	sed -i "s/%APP_VERSION%/$(APP_VERSION)/" "$(APP_NAME).6"
	sed -i "s/%APP_AUTHOR%/$(APP_AUTHOR)/" "$(APP_NAME).6"
	pandoc "$(APP_NAME).6" -s -t html -o "MAN.html"
	chmod 644 "./$(APP_NAME).6"
	chmod 644 "./MAN.html"
	chmod 644 "./README.html"

buildinstall:
	echo "#!/usr/bin/bash" > "./install.sh"
	echo "if [ ! -f \"./$(APP_NAME)\" ]; then echo 'File \"$(APP_NAME)\" not found'; exit; fi" >> "./install.sh"
	echo "sudo $(INSTALLCMD) -m 755 -b -C -D -t \"$(INSTALLDIR_BIN)\" \"./$(APP_NAME)\"" >> "./install.sh"
	echo "sudo $(INSTALLCMD) -m 644 -b -C -D -t \"$(INSTALLDIR_DOC)/$(APP_NAME)\" \"./README.html\" \"./MAN.html\"  \"./LICENSE\"" >> "./install.sh"
	echo "sudo $(INSTALLCMD) -m 644 -b -C -D -t \"$(INSTALLDIR_MAN)\" \"./$(APP_NAME).6\"" >> "./install.sh"
	echo "sudo gzip \"$(INSTALLDIR_MAN)/$(APP_NAME).6\"" >> "./install.sh"
	echo "sudo mandb" >> "./install.sh"
	chmod 755 "./install.sh"

builduninstall:
	echo "#!/usr/bin/bash" > "./uninstall.sh"
	echo "sudo rm -f \"$(INSTALLDIR_BIN)/$(APP_NAME)\"" >> "./uninstall.sh"
	echo "sudo rm -f \"$(INSTALLDIR_DOC)/$(APP_NAME)/\"*" >> "./uninstall.sh"
	echo "sudo rmdir --ignore-fail-on-non-empty \"$(INSTALLDIR_DOC)/$(APP_NAME)\"" >> "./uninstall.sh"
	echo "sudo rm -f \"$(INSTALLDIR_MAN)/$(APP_NAME).6.gz\"" >> "./uninstall.sh"
	echo "sudo mandb" >> "./uninstall.sh"
	chmod 755 "./uninstall.sh"

builddir: clean builddoc buildinstall builduninstall
	mkdir "$(DISTDIR)"
	mkdir "./$(APP_NAME)"
	cp "./install.sh" "$(APP_NAME)"/
	cp "./uninstall.sh" "$(APP_NAME)"/
	cp "./LICENSE" "$(APP_NAME)"/
	cp "./MAN.html" "$(APP_NAME)"/
	cp "./README.html" "$(APP_NAME)"/
	cp "$(APP_NAME).6" "$(APP_NAME)"/

buildpy: builddir
	-rm -f "./$(APP_NAME)/$(APP_NAME)"
	cp "./$(APP_NAME).py" "./$(APP_NAME)/$(APP_NAME)"
	chmod 755 "./$(APP_NAME)/$(APP_NAME)"

buildbin: builddir
	pyinstaller "$(APP_NAME).py" \
		--name "$(APP_NAME)" \
		--clean \
		--onefile \
		--workpath "/tmp/$(APP_NAME)_pyinstaller" \
		--specpath "/tmp/$(APP_NAME)_pyinstaller" \
		--distpath "./$(APP_NAME)" \
		--exclude-module numpy
	chmod 755 "./$(APP_NAME)/$(APP_NAME)"

packpy: builddir buildpy
	-rm -f "./$(PYTHON_PACKAGE_FILENAME)"
	tar -czvf "./$(PYTHON_PACKAGE_FILENAME)" ./$(APP_NAME)

packbin: builddir buildbin
	-rm -f "./$(BINARY_PACKAGE_FILENAME)"
	tar -czvf "./$(BINARY_PACKAGE_FILENAME)" ./$(APP_NAME)

check:
	test $(shell uname) = 'Linux'
	command -v pyinstaller
	command -v pandoc
	@echo checking minimum Python 3.9 version
	@(( $(shell python3 -c 'import sys; print(sys.version_info[0])') >= 3 ))
	@(( $(shell python3 -c 'import sys; print(sys.version_info[1])') >= 9 ))

showoptions:
	@echo "make [all] [check] [py] [bin] [clean] [distclean]"

clean:
	-find . -regex '^.*\(__pycache__\|\.py[co]\)$$' -delete
	-rm -f "./$(APP_NAME)/"*
	-rm -d -f "./$(APP_NAME)"
	-rm -R -d -f "/tmp/$(APP_NAME)_pyinstaller"
	-rm -f "./README.html"
	-rm -f "./MAN.html"
	-rm -f "./$(APP_NAME).6"
	-rm -f "./install.sh"
	-rm -f "./uninstall.sh"

distclean:
	-rm -f "$(DISTDIR)/"*
	-rm -d -f "$(DISTDIR)"

