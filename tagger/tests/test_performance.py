from edgar.classify import Classifier, Corpus
from sklearn.cross_validation import KFold
from nose.plugins.attrib import attr
from nose.tools import assert_equal
import pandas as pd
import multiprocessing
import sys


def test_kfold():
    kf = KFold(n=3, n_folds=3)
    actual = [
        {"TRAIN": list(train_index), "TEST": list(test_index)}
        for train_index, test_index in kf
        ]
    expected = [
        {'TRAIN': [1, 2], 'TEST': [0]},
        {'TRAIN': [0, 2], 'TEST': [1]},
        {'TRAIN': [0, 1], 'TEST': [2]},
    ]
    assert_equal(actual, expected)


def _train_and_test(l):
    train = l[0]
    test = l[1]
    training_paths = [Corpus.PATHS[i] for i in train]
    training = Corpus(training_paths)
    classifier = Classifier()
    classifier.fit(training.X, training.y)

    blocks = []
    for i in test:
        path = Corpus.PATHS[i]
        testing = Corpus([path])
        prediction = classifier.predict(testing.X)
        testing.lines['p_hat'] = prediction['p_hat']
        testing.lines['y_hat'] = prediction['y_hat']
        blocks.append(testing.lines)

    return pd.concat(blocks, ignore_index=True)


def my_table(df):
    means = df.groupby(['path', 'bio'])['correct'].mean()
    table = means.unstack().applymap(lambda x: round(x, 2))
    return table.sort(True)


def cross_validate_logistic_regression(n_folds=10, processes=4):
    cv = KFold(len(Corpus.PATHS), n_folds=n_folds)

    pool = multiprocessing.Pool(processes=processes)
    blocks = pool.map(_train_and_test, cv)

    lines = pd.concat(blocks, ignore_index=True)
    lines['correct'] = lines.y_hat == lines.bio

    return lines


@attr('slow')
def test_performance():
    # How well are we identifying bio regions? How many lines are we
    # missing? How many lines are false positives?
    lines = cross_validate_logistic_regression()
    write_data_for_diagnostic_graphs(lines)

    # How well are we identifying bios?


def _predict_region(block):
    lines = block.set_index('line')
    region = Classifier._optimal_region(lines.p_hat)
    path = lines.path[0]
    return {
        'folder': path.replace('corpus/', '').replace('.md', '').replace('-', '/'),
        'start': region[0],
        'stop': region[1],
    }


def write_data_for_diagnostic_graphs(lines):
    for col, dtype in lines.dtypes.iteritems():
        if dtype == 'bool':
            # Convert true / false columns to 0 / 1 columns.
            lines[col] = lines[col].astype(int)
    lines.to_csv('output/lines.csv')

    gb = lines.groupby('path')
    s = gb.apply(_predict_region)
    predictions = pd.DataFrame(list(s))
    predictions.to_csv('output/predictions.csv')

    for k in ['folder', 'start', 'stop']:
        assert k in predictions.columns
