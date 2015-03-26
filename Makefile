DATABASE = db.sqlite

create-database:
	python models.py

load-list: create-database
	Rscript 1_equilar_director_filings.R $(DATABASE)

test:
	nosetests --with-doctest
