import pandas as pd
from sqlalchemy import create_engine
import numpy as np

def names(s):
    l = s.split(', ')
    assert len(l) == 2
    return l

engine = create_engine('postgres://amarder:3NL0FmOXcT2BWnaUnbQC@iangow.me/crsp')
query = 'SELECT DISTINCT equilar_id(director_id) AS equilar_id, director_id(director_id) AS director_id, director, gender, fileyear - age AS birth_year FROM director.director;'
df = pd.read_sql(query, engine)
df['last_name'] = df.director.map(lambda s: names(s)[0])
df['first_name'] = df.director.map(lambda s: names(s)[1])
del df['director']
df['birth_year'] = df.birth_year.map(lambda x: '' if np.isnan(x) else str(int(x)))
df.to_csv('temp.csv', index=FALSE)


