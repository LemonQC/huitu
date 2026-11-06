import numpy as np
from skillcomp.utils import split_episode_ids


def test_split_is_episode_disjoint():
    ids = np.repeat(np.arange(12), 9)
    a, b = split_episode_ids(ids, val_fraction=0.25, seed=11)
    assert a.sum() + b.sum() == len(ids)
    assert not set(ids[a]).intersection(ids[b])


def test_split_is_reproducible():
    ids = np.repeat(np.arange(9), 5)
    m1, _ = split_episode_ids(ids, seed=7)
    m2, _ = split_episode_ids(ids, seed=7)
    assert np.array_equal(m1, m2)
