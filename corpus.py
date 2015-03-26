from load import Loader
import nltk
import pandas as pd
import random
import re

l = Loader()
urls = l.all_urls()

n = 10
random_urls = [random.choice(urls) for i in range(n)]
filings = l.commit_filings(random_urls)

def write(filing):
    path = filing.csv_path()
    text = filing.text().decode('utf-8')
    sentences = nltk.sent_tokenize(text)
    f = lambda s: re.sub('\s+', ' ', s)
    df = pd.DataFrame({'text': map(f, sentences), 'bio': 0})
    df.to_csv(path, encoding='utf-8', index=False)
    print path

map(write, filings)
