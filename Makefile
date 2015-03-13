DATABASE = db.sqlite

update-database:
	Rscript 1_equilar_director_filings.R $(DATABASE)
	python models.py $(DATABASE)
