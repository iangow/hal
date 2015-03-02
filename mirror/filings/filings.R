library(RPostgreSQL, quietly=TRUE)

# TODO: Pull config variables out of config.R and put them in .env
source('config.R')
config$drv <- PostgreSQL()

con <- do.call(dbConnect, config)
  sql <- paste(readLines("equilar_director_filings.sql"), collapse="\n")
  equilar_director_filings <- dbGetQuery(con, sql)
retcode <- dbDisconnect(con)

prefix <- 'http://www.sec.gov/Archives/edgar/data/'
ids <- gsub(prefix, '', equilar_director_filings$url)
cat(unique(ids), sep='\n')
