"""
Provides mapping classes to help with assortment and
    management of discord messages to functions
"""
import re
from typing import Callable, List
import discord


class Pattern:

    def __init__(self, pattern: str,
                 func: Callable[[discord.Client, discord.Message], None],
                 *, description: str = None):
        if description is None:
            self.description = '<No description>'
        else:
            self.description = description
        self.function = func
        self.pattern = pattern

    @property
    def d_pattern(self):
        # Returns a discord chat friendly pattern
        friendly = '```py\nr\'' + self.pattern + '\'```'
        return self.description + '\n' + friendly

    def matches(self, other: str):
        return bool(re.match(self.pattern, other))


def automatch(patterns: List[Pattern], message: str
              ) -> Callable[[discord.Client, discord.Message], None]:
    for pattern in patterns:
        if pattern.matches(message):
            return pattern.function
