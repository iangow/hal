import pandas as pd
from sqlalchemy import create_engine
import os
import numpy as np
import networkx as nx


def _names(s):
    l = s.split(', ')
    assert len(l) == 2
    return l


def _get_data(engine):
    query = '''
        SELECT DISTINCT
        regexp_replace(director_id, '\..*\.', '.') AS director_id,
        director, gender, fileyear - age AS birth_year
        FROM director.director;
    '''

    df = pd.read_sql(query, engine)
    df['last_name'] = df.director.map(lambda s: _names(s)[0])
    df['first_name'] = df.director.map(lambda s: _names(s)[1])
    del df['director']
    return df


def _all_edges(df):
    gb = df.groupby(['last_name', 'first_name', 'gender'])
    for k, block in gb:
        for edge in _edges(block):
            yield edge


def _edges(block):
    full = pd.merge(block, block, how='outer', suffixes=('_l', '_r'), on='gender')
    keep = (
        (full.director_id_l != full.director_id_r) &
        (np.abs(full.birth_year_l - full.birth_year_r) <= 1)
        )
    matches = full.ix[keep]
    result = [
        (row['director_id_l'], row['director_id_r'])
        for i, row in matches.iterrows()
        if row['director_id_l'] < row['director_id_r']
    ]
    return list(set(result))


def _matched_ids(edges):
    g = nx.Graph()
    g.add_edges_from(edges)
    components = list(nx.connected_components(g))
    for l in components:
        for i in l:
            for j in l:
                if i != j:
                    yield i, j


def write_matched_ids():
    engine = create_engine(os.environ['DATABASE_URL'])
    data = _get_data(engine)
    edges = _all_edges(data)
    matches = _matched_ids(edges)
    df = pd.DataFrame(data=list(matches), columns=['a', 'b'])
    df.to_sql('matched_director_ids', engine, chunksize=1000, index=False)


def write_companies():
    query = '''
        SELECT DISTINCT director.equilar_id(director_id) as equilar_id, company
        INTO companies FROM director.director;
    '''


def other_directorships(my_id):
    '''
    Note: my_id should look like '123.456' where 123 is the equilar_id
    of the firm and 456 is the director_id of the director within the
    firm.
    '''

    query = '''
        WITH x AS (
            SELECT director.equilar_id(b) AS equilar_id
            FROM matched_director_ids
            WHERE a='%s'
        )
        
        SELECT x.equilar_id, company
            FROM companies JOIN x
            ON companies.equilar_id=x.equilar_id;
        ''' % my_iq


if __name__ == '__main__':
    pass
