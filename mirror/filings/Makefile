filings.txt: filings.R
	Rscript filings.R > filings.txt
	# Remove NAs
	sed -i '/NA/d' filings.txt
