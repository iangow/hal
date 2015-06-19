postgres:
	sudo apt-get update
	sudo apt-get install postgresql postgresql-contrib postgresql-server-dev-9.3 default-jre nginx foremancli

conda:
	 wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh -O miniconda.sh
	chmod +x miniconda.sh
	./miniconda.sh -b
	echo export PATH=~/miniconda/bin:$$PATH >> ~/.bashrc
	conda update --yes conda

ENV_NAME = hal
env:
	-conda create -n $(ENV_NAME) python -y
	source activate $(ENV_NAME); \
	conda install --file conda-requirements.txt -y; \
	pip install -r requirements.txt

activate:
	echo "source activate $(ENV_NAME)"

AS_DIR = annotator-store
$(AS_DIR):
	git clone https://github.com/openannotation/annotator-store.git $(AS_DIR)
	cd $(AS_DIR); git checkout v0.13.2
	cd $(AS_DIR); source activate $(ENV_NAME); pip install -e .[flask]
	cd $(AS_DIR); cp annotator.cfg.example annotator.cfg

ES_DIR = elasticsearch-1.4.4
ES_URL = http://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.4.zip
$(ES_DIR):
	curl $(ES_URL) -o $(ES_DIR).zip
	unzip $(ES_DIR).zip
	rm $(ES_DIR).zip

install: env $(AS_DIR) $(ES_DIR)

EXPORT_VARS = $(shell cat .env | sed 's/^/export /' | tr '\n' ';')
start:
	cd $(ES_DIR); screen -S elastic-search -d -m bin/elasticsearch
	sleep 10 # Need to wait for elastic search server to boot up.
	source activate $(ENV_NAME); cd $(AS_DIR); screen -S annotator-store -d -m python run.py
	$(EXPORT_VARS); source activate $(ENV_NAME); screen -S hal -d -m python manage.py runserver

stop:
	screen -ls | grep Detached | cut -d. -f1 | awk '{print $1}' | xargs -n 1 pkill -TERM -P

edgar/filings/filings.txt:
	cd edgar/filings; make filings.txt

test:
	python manage.py test --with-doctest

load:
	cat mirror/filings/filings.txt | xargs -P 20 python manage.py load
