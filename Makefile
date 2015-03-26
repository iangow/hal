DATABASE = db.sqlite

syncdb:
	python models.py

update-database:
	Rscript 1_equilar_director_filings.R $(DATABASE)
	python models.py $(DATABASE)

test:
	nosetests --with-doctest
