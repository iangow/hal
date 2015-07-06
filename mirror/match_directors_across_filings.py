import pandas as pd
import numpy as np
import networkx as nx
from django.db import connection
from django.template.loader import render_to_string


def _names(s):
    l = s.split(', ')
    assert len(l) == 2
    return l


def get_data():
    query = '''
        SELECT DISTINCT
        regexp_replace(director_id, '\..*\.', '.') AS director_id,
        director, gender, fileyear - age AS birth_year
        FROM director;
    '''
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = ['director_id', 'director', 'gender', 'birth_year']
    df = pd.DataFrame(data=rows, columns=columns)
    df['last_name'] = df.director.map(lambda s: _names(s)[0])
    df['first_name'] = df.director.map(lambda s: _names(s)[1])
    del df['director']
    return df


def all_edges(df):
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


def matched_ids(edges):
    g = nx.Graph()
    g.add_edges_from(edges)
    components = list(nx.connected_components(g))
    for l in components:
        for i in l:
            for j in l:
                if i != j:
                    yield i, j


def create_matched_director_ids():
    data = get_data()
    edges = all_edges(data)
    matches = matched_ids(edges)
    
    pair = lambda x: "('%s', '%s')" % x
    pairs = map(pair, matches)
    values = ','.join(pairs)
    table = 'matched_director_ids'
    query = render_to_string('bulk_insert.sql', locals())
    cursor = connection.cursor()
    cursor.execute(query)
