# Highlighter

Allow user to highlight any webpage and save the results to Annotator Store.

# (edgar) Mirror

Make it easy to construct a local mirror of an external website.

# Annotator Store

I use [Annotator Store](https://github.com/openannotation/annotator-store) to record highlights in a database. `Annotator Store` is a Flask application that needs to be run in a separate process. The application depends on [ElasticSearch](http://www.elasticsearch.org/) so that needs to be running as well. I have this set up on my local machine. Next I want to check to see if I can pull data out of `ElasticSearch` easily.

## Notes on setup

```
git clone https://github.com/openannotation/annotator-store.git
cd annotator-store
git checkout v0.13.2

virtualenv pyenv
source pyenv/bin/activate
pip install -e .[flask]
cp annotator.cfg.example annotator.cfg
python run.py

wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.4.zip
```
