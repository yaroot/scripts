
PYTHON=python3.8
VENV=.venv
VBIN=${VENV}/bin

all: sync-pip

.PHONY: all

sync-pip: pip
	${VBIN}/pip-sync

.PHONY: sync-pip

pip: venv
	${VBIN}/pip install -U pip pip-tools wheel

.PHONY: pip

venv:
	test -d ${VENV} || ${PYTHON} -m venv ${VENV}

.PHONY: venv

pip-compile:
	${VBIN}/pip-compile --upgrade --rebuild

.PHONY: pip-compile
