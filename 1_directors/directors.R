library(RPostgreSQL, quietly=TRUE)
library(dplyr)

# TODO: Pull config variables out of config.R and put them in .env
source('config.R')
config$drv <- PostgreSQL()

con <- do.call(dbConnect, config)
  sql <- paste(readLines("equilar_director_filings.sql"), collapse="\n")
  equilar_director_filings <- dbGetQuery(con, sql)
retcode <- dbDisconnect(con)

## save to sqlite database
outfile <- '../db.sqlite'
create <- !file.exists(outfile)
db <- src_sqlite(outfile, create=create)
db_drop_table(db$con, 'equilar_director_filings', force=TRUE)
copy_to(db, equilar_director_filings, temporary=FALSE)
