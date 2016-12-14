SHELL   := /bin/bash
PYTHON  := /usr/bin/python3
RSYNC   := /usr/bin/rsync -azv --exclude '*~'
BROWSER := firefox

NTG_VM	   := ntg.cceh.uni-koeln.de
NTG_USER   := ntg
NTG_DB     := ntg
NTG_ROOT   := /home/$(NTG_USER)/prj/ntg/ntg
PSQL_PORT  := 5433
SERVER     := server
STATIC	   := $(SERVER)/static

TRANSLATIONS := de			 # space-separated list of translations we have eg. de fr

NTG_SERVER := $(NTG_USER)@$(NTG_VM):$(NTG_ROOT)/$(SERVER)
NTG_STATIC := $(NTG_USER)@$(NTG_VM):$(NTG_ROOT)/$(STATIC)

LESS	   := $(STATIC)/css/*.less
CSS		   := $(patsubst %.less, %.css, $(LESS))
CSS_GZ	   := $(patsubst %, %.gzip, $(CSS))

JS		   := $(STATIC)/js/*.js
JS_GZ	   := $(patsubst %, %.gzip, $(JS))

PY_SOURCES := scripts/cceh/*.py ntg_common/*.py server/*.py

.PHONY: upload upload_po update_pot update_po update_mo update_libs vpn server restart psql
.PHONY: js css jsdoc lint pylint jslint csslint

restart: js css server

server:
	server/server.py -vvv

psql:
	ssh -f -L 1$(PSQL_PORT):localhost:$(PSQL_PORT) $(NTG_USER)@$(NTG_VM) sleep 120
	sleep 1
	psql -h localhost -p 1$(PSQL_PORT) -d $(NTG_DB) -U $(NTG_USER)


lint: pylint jslint csslint

pylint:
	-pylint $(PY_SOURCES)

jslint:
	./node_modules/.bin/eslint -f unix Gruntfile.js $(JS)

csslint:
	csslint --ignore="adjoining-classes,box-sizing,ids,order-alphabetical,overqualified-elements,qualified-headings" $(CSS)

jsdoc:
	jsdoc -d jsdoc -a all $(JS) && $(BROWSER) jsdoc/index.html

bower_update:
	bower install --update

upload:
	$(RSYNC) -n $(SERVER)/server.py $(NTG_SERVER)/
	$(RSYNC) -n $(STATIC)/js $(NTG_STATIC)/js
	$(RSYNC) -n $(STATIC)/css $(NTG_STATIC)/css

css: $(CSS)

js:	$(JS)

%.css : %.less
	lessc --autoprefix="last 2 versions" $? $@

%.gzip : %
	gzip < $? > $@

### Localization ###

define LOCALE_TEMPLATE

.PRECIOUS: po/$(1).po

update_mo: server/translations/$(1)/LC_MESSAGES/messages.mo

update_po: po/$(1).po

po/$(1).po: po/server.pot
	if test -e $$@; \
	then msgmerge -U --backup=numbered $$@ $$?; \
	else msginit --locale=$(1) -i $$? -o $$@; \
	fi

server/translations/$(1)/LC_MESSAGES/messages.mo: po/$(1).po
	-mkdir -p $$(dir $$@)
	msgfmt -o $$@ $$?

endef

$(foreach lang,$(TRANSLATIONS),$(eval $(call LOCALE_TEMPLATE,$(lang))))

po/server.pot: $(PY_SOURCES) $(TEMPLATES) pybabel.cfg Makefile
	PYTHONPATH=.; pybabel extract -F pybabel.cfg --no-wrap --add-comments=NOTE \
	--copyright-holder="CCeH Cologne" --project=NTG --version=2.0 \
	--msgid-bugs-address=marcello@perathoner.de \
	-k 'l_' -k 'n_:1,2' -o $@ .

update_pot: po/server.pot