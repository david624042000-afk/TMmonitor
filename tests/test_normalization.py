from tmmonitor.utils.normalization import normalize_goods_groups


def test_normalize_goods_groups_splits_variants():
    groups = ["0301、030104, 051903", "351918\n4402", None]
    result = normalize_goods_groups(groups)
    assert result == {"0301", "030104", "051903", "351918", "4402"}
