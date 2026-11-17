"""Versioned, finite built-in syntax selections sharing the parser budgets."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Dialect:
    name: str
    version: str = '1'

    def __post_init__(self):
        if self.name not in ('commonmark', 'extended') or self.version != '1':
            raise ValueError('Select a supported built-in dialect/version.')

    @property
    def identity(self):
        return self.name + '-0.31.2-v' + self.version


COMMONMARK = Dialect('commonmark')
EXTENDED = Dialect('extended')


def select_dialect(value):
    if isinstance(value, Dialect):
        return value
    if value in ('commonmark', 'extended'):
        return COMMONMARK if value == 'commonmark' else EXTENDED
    raise ValueError('Select a supported built-in dialect.')


def dialect_identity(value=COMMONMARK):
    return select_dialect(value).identity
