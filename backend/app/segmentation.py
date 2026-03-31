from __future__ import annotations

from dataclasses import dataclass

CAMPAIGN_STARTER = "Starter"
CAMPAIGN_GROWTH = "Growth"
CAMPAIGN_PREMIUM = "Premium"
CAMPAIGN_HIGH_VALUE_YOUTH = "High Value Youth"

ALL_CAMPAIGNS = (
    CAMPAIGN_STARTER,
    CAMPAIGN_GROWTH,
    CAMPAIGN_PREMIUM,
    CAMPAIGN_HIGH_VALUE_YOUTH,
)


@dataclass(frozen=True)
class UserSegmentInput:
    age: int
    income: float


def campaigns_for_user(u: UserSegmentInput) -> set[str]:
    out: set[str] = set()
    if u.age < 30 and u.income < 3000:
        out.add(CAMPAIGN_STARTER)
    if 30 <= u.age <= 50 and 3000 <= u.income <= 10000:
        out.add(CAMPAIGN_GROWTH)
    if u.age > 50 or u.income > 10000:
        out.add(CAMPAIGN_PREMIUM)
    if u.age < 30 and u.income > 5000:
        out.add(CAMPAIGN_HIGH_VALUE_YOUTH)
    return out
