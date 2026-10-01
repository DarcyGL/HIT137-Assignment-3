import random


class GameLogic:

    def __init__(self, tiles):
        self.tiles = tiles
        self.moves = 0
        self.hints_used = 0
        self.max_hints = 3
        self.game_finished = False

    def add_move(self):
        if not self.game_finished:
            self.moves += 1

    def is_tile_correct(self, tile):
        return (
            tile.current_position == tile.original_position
            and tile.rotation % 360 == 0
            and tile.flipped is False
        )

    def count_incorrect_tiles(self):
        incorrect = 0

        for tile in self.tiles:
            if not self.is_tile_correct(tile):
                incorrect += 1

        return incorrect

    def check_puzzle_complete(self):
        if self.count_incorrect_tiles() == 0:
            self.game_finished = True
            return True

        return False

    def get_hint(self):
        if self.hints_used >= self.max_hints:
            return None

        incorrect_tiles = []

        for tile in self.tiles:
            if not self.is_tile_correct(tile):
                incorrect_tiles.append(tile)

        if len(incorrect_tiles) == 0:
            return None

        self.hints_used += 1

        return random.choice(incorrect_tiles)

    def hints_remaining(self):
        return self.max_hints - self.hints_used


    def solve_puzzle(self):
        for tile in self.tiles:

            if tile.flipped_h:
            tile.flip_horizontal()

            if tile.flipped_v:
            tile.flip_vertical()

            while tile.rotation % 360 != 0:
            tile.rotate_90()

            tile.current_position = tile.original_position

    self.moves = 0
    self.game_finished = True

    def reset_game(self, tiles):
        self.tiles = tiles
        self.moves = 0
        self.hints_used = 0
        self.game_finished = False
