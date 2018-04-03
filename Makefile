RSYNC       := /usr/bin/rsync -azv --exclude '*~'
SHELL       := /bin/bash
PYTHON      := /usr/bin/python3
MYSQL       := mysql --defaults-file=~/.my.cnf.ntg
BROWSER     := firefox

NTG_VM      := ntg.cceh.uni-koeln.de
NTG_USER    := ntg
NTG         := $(NTG_USER)@$(NTG_VM)
NTG_ROOT    := $(NTG):/home/$(NTG_USER)/prj/ntg/ntg
PSQL_PORT   := 5432
SERVER      := server
STATIC      := $(SERVER)/static

PSQL        := psql -p $(PSQL_PORT)
PGDUMP      := pg_dump -p $(PSQL_PORT)

TRANSLATIONS    := de            # space-separated list of translations we have eg. de fr

NTG_SERVER  := $(NTG_ROOT)/$(SERVER)
NTG_STATIC  := $(NTG_ROOT)/$(STATIC)

LESS        := $(wildcard $(SERVER)/less/*.less)
CSS         := $(patsubst $(SERVER)/less/%.less, $(STATIC)/css/%.css, $(LESS))
CSS_GZ      := $(patsubst %, %.gzip, $(CSS))

JS_SRC      := $(wildcard $(SERVER)/es6/*.js)
JS          := $(patsubst $(SERVER)/es6/%.js, $(STATIC)/js/%.js, $(JS_SRC))
JS_GZ       := $(patsubst %, %.gzip, $(JS))

PY_SOURCES  := scripts/cceh/*.py ntg_common/*.py server/*.py

.PHONY: upload vpn server restart psql
.PHONY: js css doc jsdoc sphinx lint pylint jslint csslint

css: $(CSS)

js:	$(JS)

restart: js css server

server: css js
	python3 -m server.server -vv

prepare:
	python3 -m scripts.cceh.prepare4cbgm -vvv server/instance/ph4.conf

users:
	scripts/cceh/mk_users.py -vvv server/instance/_global.conf

clean:
	find . -depth -name "*~" -delete

psql:
	ssh -f -L 1$(PSQL_PORT):localhost:$(PSQL_PORT) $(NTG_USER)@$(NTG_VM) sleep 120
	sleep 1
	psql -h localhost -p 1$(PSQL_PORT) -U $(NTG_USER) ntg_ph4

import_john:
	$(MYSQL) -e "DROP DATABASE DCPJohnWithFam"
	$(MYSQL) -e "CREATE DATABASE DCPJohnWithFam"
	cat ../dumps/DCPJohnWithFam-6.sql | mysql --defaults-file=~/.my.cnf.ntg -D DCPJohnWithFam

diff_affinity:
	scripts/cceh/sqldiff.sh "select ms_id1, ms_id2, affinity, common, equal, older, newer, unclear from affinity where rg_id = 94 order by ms_id1, ms_id2" | less

lint: pylint jslint csslint

pylint:
	-pylint $(PY_SOURCES)

jslint:
	./node_modules/.bin/eslint -f unix $(JS_SRC)

csslint: css
	csslint --ignore="adjoining-classes,box-sizing,ids,order-alphabetical,overqualified-elements,qualified-headings" $(CSS)

doc: sphinx

.PRECIOUS: doc_src/%.jsgraph.dot

doc_src/%.jsgraph.dot : $(STATIC)/js/%.js $(JS)
	madge --dot $< | \
	sed -e "s/static\/js\///g" \
		-e "s/static\/bower_components\///g" \
		-e "s/G {/G {\ngraph [rankdir=\"LR\"]/" > $@

doc_src/%.nolibs.jsgraph.dot : doc_src/%.jsgraph.dot
	sed -e "s/.*\/.*//g" $< > $@

%.jsgraph.png : %.jsgraph.dot
	dot -Tpng $? > $@

jsgraphs: doc_src/coherence.jsgraph.dot doc_src/comparison.jsgraph.dot \
			doc_src/coherence.nolibs.jsgraph.dot doc_src/comparison.nolibs.jsgraph.dot

sphinx: jsgraphs
	-rm docs/_images/*
	cd doc_src; make html; cd ..

jsdoc: js
	jsdoc -c jsdoc.json -d jsdoc -a all $(JS_SRC) && $(BROWSER) jsdoc/index.html

bower_update:
	bower update

upload_scripts:
	$(RSYNC) --exclude "**/__pycache__"  --exclude "*.pyc"  ntg_common $(NTG_ROOT)/
	$(RSYNC) --exclude "**/instance/**"                     server     $(NTG_ROOT)/

# from home
upload_db:
	-rm /tmp/*.pg_dump.sql.bz2
	$(PGDUMP) --clean --if-exists ntg_ph4  | bzip2 > /tmp/ntg_ph4.pg_dump.sql.bz2
	$(PGDUMP) --clean --if-exists john_ph1 | bzip2 > /tmp/john_ph1.pg_dump.sql.bz2
	scp /tmp/*.pg_dump.sql.bz2 $(NTG_USER)@$(NTG_VM):~/

# from work
copy_local_db_to_server:
	# $(PGDUMP) --clean --if-exists ntg_ph4   | psql -h $(NTG_VM) -U $(NTG_USER) ntg_ph4
	$(PGDUMP) --clean --if-exists john_ph1  | psql -h $(NTG_VM) -U $(NTG_USER) john_ph1

sqlacodegen:
	sqlacodegen mysql:///ECM_ActsPh4?read_default_group=ntg
	sqlacodegen mysql:///VarGenAtt_ActPh4?read_default_group=ntg

$(STATIC)/js/%.js : $(SERVER)/es6/%.js
	./node_modules/.bin/babel $? --out-file $@ --source-maps

$(STATIC)/js/%.js : $(SERVER)/es6/config-require.js
	cp $? $@

$(STATIC)/css/%.css : $(SERVER)/less/%.less
	lessc --global-var="BS=\"$(STATIC)/bower_components/bootstrap/less\"" --autoprefix="last 2 versions" $? $@

%.gzip : %
	gzip < $? > $@

install-prerequisites:
	sudo apt-get install apache2 libapache2-mod-wsgi-py3 \
		postgres libpg-dev postgresql-10-mysql-fdw \
		mysql default-libmysqlclient-dev \
		python3 python3-pip graphviz git plantuml
	sudo pip3 install --upgrade \
		numpy networkx matplotlib Pillow \
		psycopg2 mysqlclient sqlalchemy sqlalchemy-utils intervals \
		flask babel flask-babel flask-sqlalchemy jinja2 flask-user \
		sphinx sphinx_rtd_theme sphinx_js sphinxcontrib-plantuml
