import nltk
import pandas as pd
from models import Filing
from random_filing import Randomizer

def gen_cmp(text):
    def comp(x, y):
        extended = text + x + y
        return extended.index(x) - extended.index(y)
    return comp

def extract(filing):
    text = filing.text().decode('utf-8').lower()
    last_names = [n.lower() for n in filing._director_last_names()]
    last_names.sort(gen_cmp(text))
    
    stop_words = {
        'last_name': last_names,
        'bio_word': Filing.BIO_WORDS
    }

    d = {}
    for stop_type, l in stop_words.items():
        for word in l:
            d[word.lower()] = {
                'stop_word_type': stop_type,
                'stop_word_id': l.index(word)
            }

    sentences = nltk.sent_tokenize(text)

    data = []
    for i, sentence in enumerate(sentences):
        for word in nltk.word_tokenize(sentence):
            lowered = word.lower()
            if lowered in d:
                row = d[lowered].copy()
                row['position'] = i
                data.append(row)
    return pd.DataFrame(data)

def random_extract(randomizer, n=10):
    blocks = []
    for i in range(n):
        f = r.get_filing()
        df = extract(f)
        df['path'] = f.path()
        blocks.append(df)
    return pd.concat(blocks)

if __name__ == '__main__':
    r = Randomizer()
    df = random_extract(r, 100)
    df.to_csv('words.csv', index=False)
