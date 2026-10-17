"""Exact decimal comparison for source numeric spellings, without tolerances."""
from decimal import Decimal

NUM = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'


def exact_number(token):
    return Decimal(token)
