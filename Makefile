ENV_NAME = hal
env:
	-conda create -n $(ENV_NAME) python -y
	source activate $(ENV_NAME); \
	conda install --file conda-requirements.txt -y; \
	pip install -r requirements.txt

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
