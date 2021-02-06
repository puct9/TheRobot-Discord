"""
Provides mapping classes to help with assortment and
    management of discord messages to functions
"""
import re
from typing import Callable, List
from collections import Iterable

import discord


class Pattern:

    def __init__(self, pattern: str,
                 func: Callable[[discord.Client, discord.Message], None],
                 *, description: str = None):
        if description is None:
            self.description = '<No description>'
        else:
            self.description = description
        self.next_node = func
        self.pattern = pattern

    @property
    def d_pattern(self):
        # Returns a discord chat friendly pattern
        friendly = '```py\nr\'' + self.pattern + '\'```'
        return self.description + '\n' + friendly

    def matches(self, other: str):
        return bool(re.match(self.pattern, other))


class Endpoint:

    def __init__(self, func: Callable[[discord.Client, discord.Message], None]
                 ):
        self.function = func
        self.trace = []

    async def __call__(self, c: discord.Client, m: discord.Message):
        trace_info = '\n'.join(f'{i}: ' + t.pattern
                               for i, t in enumerate(self.trace))
        print(f'Message: {m.content}\nTrace:\n{trace_info}')
        try:
            return await self.function(c, m)
        except Exception as e:
            print(f'An exception has occurred. The message was:\n{m.content}\n'
                  'The regex filter trace is as follows:\n' +
                  trace_info +
                  f'\nThe exception is shown below:\n{e}\n')


def automatch(patterns: List[Pattern], message: str
              ) -> Callable[[discord.Client, discord.Message], None]:
    for pattern in patterns:
        if pattern.matches(message):
            if isinstance(pattern.next_node, Endpoint):
                return pattern.next_node
            return automatch(pattern.next_node, message)


# check that each path leads to an Endpoint, and there are no infinite loops
def check_walk(patterns: List[Pattern], stack: List[Pattern] = None
               ) -> None:
    if stack is None:
        stack: List[Pattern] = []
    if not all(isinstance(p, Pattern) for p in patterns):
        raise ValueError('An invalid entry exists in patterns following:\n' +
                         '\n'.join(s.pattern for s in stack))
    # go through all possible paths
    for pattern in patterns:
        if isinstance(pattern.next_node, Endpoint):
            print('Discovered an endpoint:\n' +
                  '\n'.join(s.pattern for s in stack) + ('\n' if stack else '')
                  + f'{pattern.pattern}\n')
            pattern.next_node.trace = stack + [pattern]
            yield pattern
            continue
        if not isinstance(pattern.next_node, Iterable):
            raise TypeError('An unknown object was discovered following:\n' +
                            '\n'.join(s.pattern for s in stack) + '\ninto: ' +
                            pattern.pattern)
        if pattern in stack:
            raise Exception('An indefinite loop has been found with trace:\n' +
                            '\n'.join(s.pattern for s in stack) + '\ninto: ' +
                            pattern.pattern)
        _stack = [p for p in stack]
        _stack.append(pattern)
        yield from check_walk(pattern.next_node, _stack)
