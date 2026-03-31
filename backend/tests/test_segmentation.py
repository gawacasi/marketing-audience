import pytest

from app.segmentation import (
    CAMPAIGN_GROWTH,
    CAMPAIGN_HIGH_VALUE_YOUTH,
    CAMPAIGN_PREMIUM,
    CAMPAIGN_STARTER,
    UserSegmentInput,
    campaigns_for_user,
)


def test_starter_only():
    assert campaigns_for_user(UserSegmentInput(age=25, income=2000)) == {CAMPAIGN_STARTER}


def test_growth_mid_band():
    assert campaigns_for_user(UserSegmentInput(age=40, income=5000)) == {CAMPAIGN_GROWTH}


def test_premium_age():
    assert campaigns_for_user(UserSegmentInput(age=55, income=1000)) == {CAMPAIGN_PREMIUM}


def test_premium_income():
    assert campaigns_for_user(UserSegmentInput(age=40, income=15000)) == {CAMPAIGN_PREMIUM}


def test_high_value_youth():
    assert campaigns_for_user(UserSegmentInput(age=25, income=6000)) == {
        CAMPAIGN_PREMIUM,
        CAMPAIGN_HIGH_VALUE_YOUTH,
    }


def test_overlap_premium_and_hvy():
    assert campaigns_for_user(UserSegmentInput(age=25, income=12000)) == {
        CAMPAIGN_PREMIUM,
        CAMPAIGN_HIGH_VALUE_YOUTH,
    }


def test_boundary_age_30_growth_not_starter():
    assert CAMPAIGN_STARTER not in campaigns_for_user(UserSegmentInput(age=30, income=4000))
    assert CAMPAIGN_GROWTH in campaigns_for_user(UserSegmentInput(age=30, income=4000))


def test_boundary_income_3000_growth():
    assert CAMPAIGN_GROWTH in campaigns_for_user(UserSegmentInput(age=40, income=3000))


def test_boundary_income_10000_growth():
    assert CAMPAIGN_GROWTH in campaigns_for_user(UserSegmentInput(age=40, income=10000))


def test_starter_upper_bound_income():
    assert CAMPAIGN_STARTER in campaigns_for_user(UserSegmentInput(age=20, income=2999.99))


@pytest.mark.parametrize(
    "age,income,expected",
    [
        (29, 2999, {CAMPAIGN_STARTER}),
        (29, 3000, set()),
        (29, 5001, {CAMPAIGN_HIGH_VALUE_YOUTH}),
        (29, 12000, {CAMPAIGN_PREMIUM, CAMPAIGN_HIGH_VALUE_YOUTH}),
    ],
)
def test_edge_cases(age, income, expected):
    assert campaigns_for_user(UserSegmentInput(age=age, income=income)) == expected
