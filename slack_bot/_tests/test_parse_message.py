"""
Tests message parseing
"""


from slack_bot import get_sum_from_message, ParseError

from pytest import raises


def test_parse():
    eg_message = "!rent eweb: $134.01 sanipac: $133.49 Gas: $133.29 Elle-555"
    tot, adjust = get_sum_from_message(eg_message)
    assert tot == 13401 + 13349 + 13329
    assert tuple(adjust.items()) == (("Elle", 555_00),)


def test_fail():
    eg_message = "!rent eweb: $134.01 sani-pac: $133.49 Gas: $133.29 Elle-555"
    with raises(ParseError) as e:
        tot, adjust = get_sum_from_message(eg_message)
        assert e.bad_word == "sani-pac"


if __name__ == "__main__":
    test_fail()
