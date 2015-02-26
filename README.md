# HAL

![HAL9000](http://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/HAL9000.svg/256px-HAL9000.svg.png)

I want to create a program that consumes highlighted documents, learns from the corpus, and does a reasonable job at highlighting future documents. To start I need to figure out how to pull data out of `ElasticSearch`.

## Highlighter

Allow user to highlight any webpage and save the results to Annotator Store.

### es.py

Added some code to pull the important parts of the highlight data out of `ElasticSearch`. I'll probably turn this into a management command so we can quickly copy data from `ElasticSearch` into the SQL database.

## (edgar) Mirror

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
