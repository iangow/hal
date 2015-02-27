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
