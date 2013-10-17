#test:
#	true
#
#install:
#	python setup.py install
#
#build:
#	python setup.py build
#
#sdist:
#	python setup.py sdist
#
#upload:
#	python setup.py sdist upload

clean:
	rm -rf dist build *.egg-info flaskwallet-*
	rm -rf .coverage coverage

.PHONY: css
css: static/css/wallet.css
static/css/wallet.css: static/css/*sass
	sass static/css/wallet.sass:static/css/wallet.css

BOXV=0.7.2
BOXDIR=bitcoin-testnet-box-${BOXV}/
v${BOXV}.tar.gz:
	wget https://github.com/freewil/bitcoin-testnet-box/archive/v${BOXV}.tar.gz

${BOXDIR}: v${BOXV}.tar.gz
	tar xvzf v${BOXV}.tar.gz

.PHONY: boxstart
boxstart: ${BOXDIR}
	make -C ${BOXDIR} start

.PHONY: boxstop
boxstop: ${BOXDIR}
	make -C ${BOXDIR} stop

.PHONY: boxclean
boxclean: ${BOXDIR}
	make -C ${BOXDIR} clean

.PHONY: test
test:
	python tests.py --failfast
	python otpapp/tests.py --failfast
	python settingsapp/tests.py --failfast
	python walletapp/tests.py --failfast

.PHONY: .coverage
.coverage:
	coverage run tests.py
	coverage run -a otpapp/tests.py
	coverage run -a settingsapp/tests.py
	coverage run -a walletapp/tests.py

coverage: .coverage
	coverage html --omit "*/tests.py","*/__init__.py",main.py,config_template.py -d coverage

DB=flaskwallet

.PHONY: dump
dump: ${DB}.sql

${DB}.sql:
	sqlite3 ${DB}.db .dump > ${DB}.sql

.PHONY: load
load:
	cat ${DB}.sql | sqlite3 ${DB}.db
