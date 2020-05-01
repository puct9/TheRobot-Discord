"""
Holds the necessary classes and methods for the game of connect-4
Game is played on a position with 7 columns and 6 rows
dumbed down version of what you would find in one of my other repos lol
"""
import json
from typing import Iterable, Tuple

import numpy as np


class C4Game:

    def __init__(self) -> None:
        # initialise history, game state
        # game state representation as a 2d array, column by column
        self.move_history = []
        self.position = np.zeros((7, 6), dtype=int)
        self.to_move = -1  # -1 p1 to move, 1 is p2 to move

    @classmethod
    def deserialise(cls, info_dict) -> 'C4Game':
        g = cls()
        g.move_history = info_dict['move_history']
        g.position = np.array(info_dict['position'])
        g.to_move = info_dict['to_move']
        return g

    @classmethod
    def find_four(cls, span: Iterable) -> bool:
        """
        Parameters
        ----------
        span: `Iterable`
            An iterable with same type items implementing __eq__
        Returns
        -------
        contiguous_four: `bool`
            True if there are is a section of a contiguous set of 4 of the
            same item, as checked by __eq__
        """
        looking_for = None
        contiguous = 1
        for c in span:
            if not c:
                contiguous = 0
                continue
            if looking_for is None:
                looking_for = c
                contiguous = 1
            elif looking_for == c:
                contiguous += 1
                if contiguous == 4:
                    return True
            else:  # != c
                looking_for = c
                contiguous = 1
        return False

    def simple_state(self) -> int:
        """
        Returns
        -------
        ret: `int`
            Unique integer representing state
        """
        # 85 bits required
        # 84 bits for position
        # 1 bit for turn (kind of redundant, but why not)
        # maybe player sets up some strange position
        ret = 0
        for r, row in enumerate(self.position):
            for c, v in enumerate(row):
                if v == -1:
                    ret |= 1 << 42 + r * 7 + c
                elif v == 1:
                    ret |= 1 << r * 7 + c
        if self.to_move == -1:
            ret |= 1 << 84
        return ret

    def legal_moves(self) -> Tuple[int, int, int, int, int, int, int]:
        """
        Returns
        -------
        ret: `Tuple[int, int, int, int, int, int, int]`
            A 7-tuple of ints where 1 is legal to move and 0 is not
        """
        return tuple(int(x[-1] == 0) for x in self.position)

    def play_move(self, col: int) -> None:
        """
        Parameters
        ----------
        col: `int`
            The column of which the piece would be played
        Returns
        -------
        ret: `None`
        Raises
        ------
        `IndexError`
            The `col` argument is out of range of the columns
        `ValueError`
            The column specified is fully occupied
        """
        if not 0 <= col < 7:
            raise IndexError(f'Out of range column {col}')
        for i, c in enumerate(self.position[col]):
            if not c:
                self.position[col, i] = self.to_move
                self.to_move *= -1
                return
        raise ValueError(f'Column is fully occupied')

    def check_terminal(self) -> bool:
        """
        Returns
        -------
        term:
            1 if 4 in a row is present on the board else 0 if draw else None
        """
        # check columns
        for col in self.position:
            # start from the bottom of the column (index 0)
            if C4Game.find_four(col):
                return 1
        # check rows
        for i in range(6):
            if C4Game.find_four(self.position[:, i]):
                return 1
        # check diagonals
        flipped = np.fliplr(self.position)
        for i in range(-3, 3):
            # main diagonal
            if C4Game.find_four(self.position.diagonal(i)):
                return 1
            # non-main diagonal
            if C4Game.find_four(flipped.diagonal(i)):
                return 1
        # check board full
        if not any(self.legal_moves()):
            return 0
        return None

    def serialise(self) -> dict:
        return {
            'move_history': self.move_history,
            'position': self.position.astype(int).tolist(),
            'to_move': self.to_move
        }

    def discord_message(self) -> str:
        ret = ''
        for row in range(6):
            sub = self.position[:, 5 - row]
            mapping = [':blue_circle:', ':yellow_circle:', ':red_circle:']
            ret += ' '.join(mapping[x] for x in sub)
            ret += '\n'
        chars = 'abcdefg'
        ret += ' '.join(f':regional_indicator_{c}:' for c in chars)
        return ret

    def string_serialise(self) -> str:
        ret = ''
        for row in range(6):
            sub = self.position[:, 5 - row]
            mapping = ['1', 'o', 'x']
            ret += ''.join(mapping[x] for x in sub)
            ret += '/'
        return ret[:-1]

    def __str__(self) -> str:
        """
        Returns
        -------
        ret: `str`
            String representation of the current state
        """
        ret = ''
        for row in range(6):
            sub = self.position[:, 5 - row]
            data = '| '
            data += ' | '.join('X' if x == -1 else 'O'
                               if x == 1 else ' ' for x in sub)
            data += ' |'
            ret += data + '\n'
        ret += '-' * (len(ret) // 6 - 1)
        return ret + '\n  0   1   2   3   4   5   6'

    def __repr__(self) -> str:
        """
        Returns
        -------
        ret: `str`
            String representation of the current state, plus ID of object
        """
        return f'{str(self)}\nid={str(id(self))}'
