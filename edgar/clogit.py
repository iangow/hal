import pandas as pd
import numpy as np
from StringIO import StringIO
from nose.tools import assert_almost_equal


def log_loss(y, p, epsilon=1e-15):
    '''
    Assumes that exactly once class is chosen for each observation.
    '''
    # Make sure the predicted probabilities are within (0, 1).
    p = np.maximum(epsilon, p)
    p = np.minimum(p, 1-epsilon)

    return -1.0/sum(y) * sum(y * np.log(p))


def test_log_loss():
    data = '''id,y,p,choice
1,1,0.5,1
2,1,0.1,1
3,1,0.01,1
4,0,0.9,1
5,0,0.75,1
6,0,0.001,1
1,0,0.5,2
2,0,0.9,2
3,0,0.99,2
4,1,0.1,2
5,1,0.25,2
6,1,0.999,2'''
    f = StringIO(data)
    df = pd.DataFrame.from_csv(f)
    actual = log_loss(df.y, df.p)
    expected = 1.881797069
    assert_almost_equal(actual, expected)


test_log_loss()
