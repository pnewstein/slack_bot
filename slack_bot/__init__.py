"""
a bot for transparently calculating rent due
"""
from __future__ import annotations
import re

from . import calc_rent


class ParseError(Exception):
    def __init__(self, bad_word):
        self.bad_word = bad_word

def get_sum_from_message(message: str) -> tuple[int, dict[str, int]]:
    """
    gets all of the numbers, assumes they are in dollars
    returns the number of cents of the sum
    """
    numbers: list[int] = []
    adjustments: dict[str, int] = {}
    for word in message.split():
        # take out adjustments
        if "-" in word:
            word_parts = word.split("-")
            if len(word_parts) != 2:
                continue
            name, adj_str = word_parts
            try:
                adjustments[name] = int(float(adj_str) * 100)
            except ValueError as e:
                raise ParseError(word) from e

        no_money = word.strip("$")
        try:
            numbers.append(int(float(no_money) * 100))
        except ValueError:
            pass
    return sum(numbers), adjustments
