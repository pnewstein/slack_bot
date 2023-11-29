"""
Tests rent calculation module
"""

from pathlib import Path
import json

import slack_bot


def test_get_rent_to_pay():
    out = slack_bot.calc_rent.get_rent_to_pay(100_00, 1)
    assert out == 100_00
    out = slack_bot.calc_rent.get_rent_to_pay(100_00, 0.5)
    assert out == 50_00
    out = slack_bot.calc_rent.get_rent_to_pay(100_00, 0.01)
    assert out == 0


def test_render_json():
    cd = slack_bot.calc_rent.ConfigData.fromDict(
        json.loads(Path("empty_split.json").read_text("utf-8"))
    )
    out = slack_bot.calc_rent.calculate_rent_due(cd, set(), 1000_00)
    print(out)


if __name__ == "__main__":
    test_render_json()
