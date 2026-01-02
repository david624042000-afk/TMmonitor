from tmmonitor.services.prefilter import has_goods_group_intersection


def test_prefilter_intersection():
    groups_a = ["0301, 030104", "4402"]
    groups_b = ["051903", "030104"]
    assert has_goods_group_intersection(groups_a, groups_b) is True


def test_prefilter_no_intersection():
    groups_a = ["0301"]
    groups_b = ["4402"]
    assert has_goods_group_intersection(groups_a, groups_b) is False
