# image_processor.py
# Handles loading, slicing, transforming, and reassembling images for the
# tile-scramble puzzle. Image Processing part (Dhruv).

import os
import random
import cv2
import numpy as np


class Tile:
    """Represents a single puzzle tile: its image data, its correct home
    position, and its current rotation/flip state.

    Field names match what game_logic.py (Darcy) expects:
    - current_position / original_position: (row, col) tuples
    - rotation: degrees clockwise (0, 90, 180, 270)
    - flipped: True if flipped on EITHER axis (for GameLogic's is_tile_correct)
    Internally we still track flipped_h / flipped_v separately, since solve_puzzle
    needs to know which axis to reverse -- 'flipped' is just a convenience
    property derived from those two.
    """

    def __init__(self, image: np.ndarray, correct_row: int, correct_col: int):
        self.image = image
        self.original_position = (correct_row, correct_col)
        self.current_position = (correct_row, correct_col)
        self.rotation = 0
        self.flipped_h = False
        self.flipped_v = False

    @property
    def flipped(self) -> bool:
        """True if flipped on either axis. Read-only convenience for GameLogic."""
        return self.flipped_h or self.flipped_v

    def rotate_90(self):
        """Rotate this tile 90 degrees clockwise."""
        self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        self.rotation = (self.rotation + 90) % 360

    def flip_horizontal(self):
        self.image = cv2.flip(self.image, 1)
        self.flipped_h = not self.flipped_h

    def flip_vertical(self):
        self.image = cv2.flip(self.image, 0)
        self.flipped_v = not self.flipped_v

    def is_correct(self) -> bool:
        """True if this tile is in its correct position AND correct orientation.
        Kept here too so Tile is self-sufficient, even though GameLogic has
        its own is_tile_correct() that checks the same thing externally."""
        return (
            self.current_position == self.original_position
            and self.rotation % 360 == 0
            and not self.flipped
        )


def load_image(filepath: str) -> np.ndarray:
    """Loads an image from disk. Raises ValueError if the file doesn't exist
    or isn't a readable image."""
    if not os.path.exists(filepath):
        raise ValueError(f"File not found: {filepath}")

    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    if not filepath.lower().endswith(valid_extensions):
        raise ValueError(f"Unsupported file type: {filepath}")

    image = cv2.imread(filepath)
    if image is None:
        raise ValueError(f"Could not read image (corrupt or invalid): {filepath}")

    return image


def resize_and_pad(image: np.ndarray, grid_size: int, max_dim: int = 600) -> np.ndarray:
    """Resize and pad the image to a square so tiles can rotate correctly."""

    h, w = image.shape[:2]

    # Resize image to fit within max_dim x max_dim
    scale = min(max_dim / w, max_dim / h)

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized = cv2.resize(image, (new_w, new_h))

    # Pad image to make it square
    top = (max_dim - new_h) // 2
    bottom = max_dim - new_h - top

    left = (max_dim - new_w) // 2
    right = max_dim - new_w - left

    padded = cv2.copyMakeBorder(
        resized,
        top,
        bottom,
        left,
        right,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0)
    )

    return padded


def slice_into_tiles(image: np.ndarray, grid_size: int) -> list:
    """Cuts the image into grid_size x grid_size tiles, returned as a flat
    list of Tile objects in row-major order."""
    h, w = image.shape[:2]
    tile_h = h // grid_size
    tile_w = w // grid_size

    tiles = []
    for row in range(grid_size):
        for col in range(grid_size):
            y0, y1 = row * tile_h, (row + 1) * tile_h
            x0, x1 = col * tile_w, (col + 1) * tile_w
            tile_image = image[y0:y1, x0:x1].copy()
            tiles.append(Tile(tile_image, row, col))

    return tiles


def scramble_tiles(tiles: list, grid_size: int) -> list:
    """Applies random swap/rotate/flip transformations to the tiles. Number
    of transformations scales with grid size (6 for 3x3, 12 for 4x4, 20 for 5x5)."""
    transform_counts = {3: 6, 4: 12, 5: 20}
    num_transforms = transform_counts.get(grid_size, grid_size * 2)

    for _ in range(num_transforms):
        transform_type = random.choice(['swap', 'rotate', 'flip'])

        if transform_type == 'swap':
            i, j = random.sample(range(len(tiles)), 2)
            tiles[i].current_position, tiles[j].current_position = (
                tiles[j].current_position, tiles[i].current_position
            )
            tiles[i], tiles[j] = tiles[j], tiles[i]

        elif transform_type == 'rotate':
            tile = random.choice(tiles)
            times = random.choice([1, 2, 3])  # 90, 180, or 270 degrees
            for _ in range(times):
                tile.rotate_90()

        elif transform_type == 'flip':
            tile = random.choice(tiles)
            if random.choice([True, False]):
                tile.flip_horizontal()
            else:
                tile.flip_vertical()

    return tiles


def reassemble_image(tiles: list, grid_size: int) -> np.ndarray:
    """Stitches the current state of all tiles back into one full image,
    based on each tile's CURRENT position (not correct position)."""
    grid = [[None] * grid_size for _ in range(grid_size)]
    for tile in tiles:
        row, col = tile.current_position
        grid[row][col] = tile.image

    rows = [np.hstack(grid[r]) for r in range(grid_size)]
    return np.vstack(rows)


def load_and_process_image(filepath: str, grid_size: int) -> tuple:
    """Main entry point Dishana's GUI calls. Returns (original_image, tiles)
    ready for display. Raises ValueError on any invalid input."""
    if grid_size not in (3, 4, 5):
        raise ValueError(f"Invalid grid size: {grid_size}. Must be 3, 4, or 5.")

    image = load_image(filepath)
    processed = resize_and_pad(image, grid_size)
    tiles = slice_into_tiles(processed, grid_size)
    scrambled_tiles = scramble_tiles(tiles, grid_size)

    return processed, scrambled_tiles
