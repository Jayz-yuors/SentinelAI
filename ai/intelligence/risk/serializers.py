import json

from ai.intelligence.risk.risk_profile import (
    RiskProfile,
)


def profile_to_dict(
    profile: RiskProfile,
) -> dict:

    return profile.to_dict()


def profile_to_json(
    profile: RiskProfile,
) -> str:

    return json.dumps(
        profile.to_dict(),
        indent=2,
        default=str,
    )