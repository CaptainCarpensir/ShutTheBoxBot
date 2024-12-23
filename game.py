import random
from enum import Enum

import numpy as np

from helpers import SumsTable


class GameState(Enum):
    ROLL = 1
    FLIP_BOXES = 2
    LOSE = 3
    WIN = 4


class ShutTheBoxGame:
    def __init__(self, num_faces: int, num_die: int):
        if (num_faces < 1 or num_die < 1):
            raise ValueError("The number of faces and die can only be natural numbers")

        self.num_faces = num_faces
        self.num_die = num_die
        self.game_state = GameState.ROLL
        self.curr_die_rem = 0
        self.sums_table = SumsTable()

        self.boxes_closed = np.full(num_die * num_faces, False)

    def __are_sums_possible(self, x: int) -> bool:
        # Get combinations of possible sums of die roll
        sums = self.sums_table.get_all_sums(x)

        # Check if any of the sums are possible
        any_possible = False
        for possible_sum in sums:
            this_sum_possible = True
            for num in possible_sum:
                # Convert from 1-indexed to 0-indexed
                # If box is already closed, the sum is not possible
                if self.boxes_closed[num - 1]:
                    this_sum_possible = False
            if this_sum_possible:
                any_possible = True

        return any_possible

    def handle_roll(self):
        if (self.game_state != GameState.ROLL):
            raise ValueError("Incorrect state")

        # Roll die

        sum = 0
        for _ in range(self.num_die):
            sum += random.randint(1, self.num_faces)
        self.curr_die_rem = sum

        if self.__are_sums_possible(self.curr_die_rem):
            self.game_state = GameState.FLIP_BOXES
        else:
            self.game_state = GameState.LOSE

    def handle_flip(self, box_to_flip: int):
        if (self.game_state != GameState.FLIP_BOXES):
            raise ValueError("Incorrect state")

        if box_to_flip not in self.get_possible_flips():
            raise ValueError("Illegal box to flip")

        # Convert from 1-indexed to 0-indexed
        box_index = box_to_flip - 1

        # Flip box and subtract value
        self.boxes_closed[box_index] = True
        self.curr_die_rem -= box_to_flip

        if self.curr_die_rem == 0 and all(self.boxes_closed):
            self.game_state = GameState.WIN
        elif self.curr_die_rem == 0:
            self.game_state = GameState.ROLL
        elif not self.__are_sums_possible(self.curr_die_rem):
            self.game_state = GameState.LOSE

    def get_die_remaining(self):
        return self.curr_die_rem

    def get_boxes_closed(self):
        return self.boxes_closed

    def get_nums_closed(self) -> list:
        closed = self.get_boxes_closed()
        return [x for x in range(1, len(closed) + 1) if closed[x - 1]]

    def get_possible_flips(self):
        flips = []
        closed_nums = self.get_nums_closed()
        all_sums = self.sums_table.get_all_sums(self.curr_die_rem)
        for sums in all_sums:
            if set(sums).intersection(set(closed_nums)):
                continue
            for num in sums:
                if num not in flips and not self.boxes_closed[num - 1]:
                    flips.append(num)
        flips.sort()
        return flips

    def get_game_state(self):
        return self.game_state
