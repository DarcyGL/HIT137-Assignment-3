import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2

from image_processor import load_and_process_image, reassemble_image
from game_logic import GameLogic


class PuzzleGUI:
    """Graphical interface for the image puzzle game."""

    def __init__(self, root):
        self.root = root
        self.root.title("Image Puzzle Game")
        self.root.geometry("1100x700")

        # Image data
        self.original_image = None
        self.original_photo = None
        self.puzzle_photo = None
        self.image_path = None

        # Puzzle data
        self.tiles = []
        self.game = None
        self.selected_tile = None
        self.hint_tile = None

        # Puzzle display measurements
        self.puzzle_display_width = 0
        self.puzzle_display_height = 0
        self.puzzle_x_offset = 0
        self.puzzle_y_offset = 0

        # Original image display measurements
        self.original_display_width = 0
        self.original_display_height = 0
        self.original_x_offset = 0
        self.original_y_offset = 0

        self.create_widgets()

    def create_widgets(self):
        """Create the GUI widgets."""

        title_label = tk.Label(
            self.root,
            text="Image Puzzle Game",
            font=("Arial", 22, "bold")
        )
        title_label.pack(pady=15)

        # Top controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        grid_label = tk.Label(
            control_frame,
            text="Grid Size:",
            font=("Arial", 11)
        )
        grid_label.grid(row=0, column=0, padx=5)

        self.grid_size = tk.StringVar(value="3 x 3")

        self.grid_box = ttk.Combobox(
            control_frame,
            textvariable=self.grid_size,
            values=["3 x 3", "4 x 4", "5 x 5"],
            state="readonly",
            width=8
        )
        self.grid_box.grid(row=0, column=1, padx=5)

        self.load_button = tk.Button(
            control_frame,
            text="Load Image",
            width=12,
            command=self.load_image
        )
        self.load_button.grid(row=0, column=2, padx=10)

        self.hint_button = tk.Button(
            control_frame,
            text="Hint",
            width=10,
            command=self.show_hint
        )
        self.hint_button.grid(row=0, column=3, padx=10)

        self.solve_button = tk.Button(
            control_frame,
            text="Solve",
            width=10,
            command=self.solve_puzzle
        )
        self.solve_button.grid(row=0, column=4, padx=10)

        # Status information
        score_frame = tk.Frame(self.root)
        score_frame.pack(pady=10)

        self.moves_label = tk.Label(
            score_frame,
            text="Moves: 0",
            font=("Arial", 11, "bold")
        )
        self.moves_label.grid(row=0, column=0, padx=20)

        self.incorrect_label = tk.Label(
            score_frame,
            text="Tiles Incorrect: 0",
            font=("Arial", 11, "bold")
        )
        self.incorrect_label.grid(row=0, column=1, padx=20)

        self.hints_label = tk.Label(
            score_frame,
            text="Hints Remaining: 3",
            font=("Arial", 11, "bold")
        )
        self.hints_label.grid(row=0, column=2, padx=20)

        # Image area
        image_frame = tk.Frame(self.root)
        image_frame.pack(
            expand=True,
            fill="both",
            padx=20,
            pady=10
        )

        # Original image
        original_frame = tk.Frame(image_frame)
        original_frame.pack(
            side="left",
            expand=True
        )

        original_label = tk.Label(
            original_frame,
            text="Original Image",
            font=("Arial", 14, "bold")
        )
        original_label.pack(pady=5)

        self.original_canvas = tk.Canvas(
            original_frame,
            width=400,
            height=400,
            bg="lightgray"
        )
        self.original_canvas.pack()

        # Puzzle image
        puzzle_frame = tk.Frame(image_frame)
        puzzle_frame.pack(
            side="right",
            expand=True
        )

        puzzle_label = tk.Label(
            puzzle_frame,
            text="Puzzle",
            font=("Arial", 14, "bold")
        )
        puzzle_label.pack(pady=5)

        self.puzzle_canvas = tk.Canvas(
            puzzle_frame,
            width=400,
            height=400,
            bg="lightgray"
        )
        self.puzzle_canvas.pack()

        # Mouse controls
        self.puzzle_canvas.bind(
            "<Button-1>",
            self.on_left_click
        )

        self.puzzle_canvas.bind(
            "<Button-3>",
            self.on_right_click
        )

        self.puzzle_canvas.bind(
            "<Shift-Button-1>",
            self.on_shift_left_click
        )

        # Instructions
        instructions = tk.Label(
            self.root,
            text=(
                "Left Click: Select / Swap     |     "
                "Right Click: Rotate     |     "
                "Shift + Left Click: Flip"
            ),
            font=("Arial", 10)
        )
        instructions.pack(pady=10)

    def load_image(self):
        """Load an image and create a new puzzle."""

        file_path = filedialog.askopenfilename(
            title="Choose an Image",
            filetypes=[
                ("PNG Files", "*.png"),
                ("JPEG Files", "*.jpg"),
                ("JPEG Files", "*.jpeg"),
                ("BMP Files", "*.bmp"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        if not file_path:
            return

        try:
            grid_size = int(
                self.grid_size.get().split()[0]
            )

            original, tiles = load_and_process_image(
                file_path,
                grid_size
            )


            self.image_path = file_path
            self.original_image = original
            self.tiles = tiles

            self.selected_tile = None
            self.hint_tile = None

            if self.game is None:
                self.game = GameLogic(self.tiles)
            else:
                self.game.reset_game(self.tiles)

            self.display_original()

            self.display_puzzle()

            self.update_status()

        except Exception as error:
            messagebox.showerror(
                "Image Error",
                "The image could not be loaded.\n\n"
                + str(error)
            )

    def display_original(self):
        """Display the original image."""

        if self.original_image is None:
            return

        rgb_image = cv2.cvtColor(
            self.original_image,
            cv2.COLOR_BGR2RGB
        )

        pil_image = Image.fromarray(rgb_image)
        pil_image.thumbnail((400, 400))

        self.original_display_width = pil_image.width
        self.original_display_height = pil_image.height

        self.original_x_offset = (
            400 - self.original_display_width
        ) / 2

        self.original_y_offset = (
            400 - self.original_display_height
        ) / 2

        self.original_photo = ImageTk.PhotoImage(
            pil_image
        )

        self.original_canvas.delete("all")

        self.original_canvas.create_image(
            200,
            200,
            image=self.original_photo,
            anchor="center"
        )

        if self.hint_tile is not None:
            self.draw_original_hint()

    def display_puzzle(self):
        """Display the current puzzle."""

        if not self.tiles:
            return

        grid_size = int(
            self.grid_size.get().split()[0]
        )

        puzzle_image = reassemble_image(
            self.tiles,
            grid_size
        )

        rgb_image = cv2.cvtColor(
            puzzle_image,
            cv2.COLOR_BGR2RGB
        )

        pil_image = Image.fromarray(rgb_image)
        pil_image.thumbnail((400, 400))

        self.puzzle_display_width = pil_image.width
        self.puzzle_display_height = pil_image.height

        self.puzzle_x_offset = (
            400 - self.puzzle_display_width
        ) / 2

        self.puzzle_y_offset = (
            400 - self.puzzle_display_height
        ) / 2

        self.puzzle_photo = ImageTk.PhotoImage(
            pil_image
        )

        self.puzzle_canvas.delete("all")

        self.puzzle_canvas.create_image(
            200,
            200,
            image=self.puzzle_photo,
            anchor="center"
        )

        self.draw_grid()
        self.draw_correct_ticks()

        if self.selected_tile is not None:
            self.draw_selection()

        if self.hint_tile is not None:
            self.draw_puzzle_hint()

    def draw_grid(self):
        """Draw faint grid lines on the puzzle."""

        grid_size = int(
            self.grid_size.get().split()[0]
        )

        tile_width = (
            self.puzzle_display_width / grid_size
        )

        tile_height = (
            self.puzzle_display_height / grid_size
        )

        for i in range(1, grid_size):
            x = (
                self.puzzle_x_offset
                + i * tile_width
            )

            self.puzzle_canvas.create_line(
                x,
                self.puzzle_y_offset,
                x,
                self.puzzle_y_offset
                + self.puzzle_display_height,
                fill="gray",
                width=1
            )

        for i in range(1, grid_size):
            y = (
                self.puzzle_y_offset
                + i * tile_height
            )

            self.puzzle_canvas.create_line(
                self.puzzle_x_offset,
                y,
                self.puzzle_x_offset
                + self.puzzle_display_width,
                y,
                fill="gray",
                width=1
            )

    def get_clicked_position(self, event):
        """Convert a mouse click into a puzzle row and column."""

        if not self.tiles:
            return None

        if (
            event.x < self.puzzle_x_offset
            or event.x >= (
                self.puzzle_x_offset
                + self.puzzle_display_width
            )
            or event.y < self.puzzle_y_offset
            or event.y >= (
                self.puzzle_y_offset
                + self.puzzle_display_height
            )
        ):
            return None

        grid_size = int(
            self.grid_size.get().split()[0]
        )

        tile_width = (
            self.puzzle_display_width / grid_size
        )

        tile_height = (
            self.puzzle_display_height / grid_size
        )

        col = int(
            (event.x - self.puzzle_x_offset)
            / tile_width
        )

        row = int(
            (event.y - self.puzzle_y_offset)
            / tile_height
        )

        return row, col

    def get_tile_at_position(self, position):
        """Find the tile currently occupying a position."""

        for tile in self.tiles:
            if tile.current_position == position:
                return tile

        return None

    def on_left_click(self, event):
        """Select a tile or swap two tiles."""

        if self.game is None:
            return

        if self.game.game_finished:
            return

        position = self.get_clicked_position(event)

        if position is None:
            return

        clicked_tile = self.get_tile_at_position(
            position
        )

        if clicked_tile is None:
            return

        # First click selects a tile
        if self.selected_tile is None:
            self.selected_tile = clicked_tile
            self.display_puzzle()
            return

        # Clicking the selected tile again deselects it
        if self.selected_tile is clicked_tile:
            self.selected_tile = None
            self.display_puzzle()
            return

        # Swap positions
        first_position = (
            self.selected_tile.current_position
        )

        second_position = (
            clicked_tile.current_position
        )

        self.selected_tile.current_position = (
            second_position
        )

        clicked_tile.current_position = (
            first_position
        )

        self.selected_tile = None

        self.complete_move()

    def on_right_click(self, event):
        """Rotate a tile 90 degrees clockwise."""

        if self.game is None:
            return

        if self.game.game_finished:
            return

        position = self.get_clicked_position(event)

        if position is None:
            return

        tile = self.get_tile_at_position(position)

        if tile is None:
            return

        tile.rotate_90()

        self.selected_tile = None

        self.complete_move()

    def on_shift_left_click(self, event):
        """Flip a tile horizontally."""

        if self.game is None:
            return "break"

        if self.game.game_finished:
            return "break"

        position = self.get_clicked_position(event)

        if position is None:
            return "break"

        tile = self.get_tile_at_position(position)

        if tile is None:
            return "break"

        tile.flip_horizontal()

        self.selected_tile = None

        self.complete_move()

        return "break"

    def complete_move(self):
        """Update the game after a player move."""

        if self.game is None:
            return

        self.game.add_move()

        # A hint disappears after the next move
        self.hint_tile = None

        self.display_original()
        self.display_puzzle()
        self.update_status()

        if self.game.check_puzzle_complete():
            self.update_status()

            messagebox.showinfo(
                "Puzzle Complete",
                (
                    "Congratulations!\n\n"
                    "You completed the puzzle in "
                    f"{self.game.moves} moves."
                )
            )

    def draw_selection(self):
        """Draw a blue outline around the selected tile."""

        if self.selected_tile is None:
            return

        grid_size = int(
            self.grid_size.get().split()[0]
        )

        row, col = (
            self.selected_tile.current_position
        )

        tile_width = (
            self.puzzle_display_width / grid_size
        )

        tile_height = (
            self.puzzle_display_height / grid_size
        )

        x1 = (
            self.puzzle_x_offset
            + col * tile_width
        )

        y1 = (
            self.puzzle_y_offset
            + row * tile_height
        )

        x2 = x1 + tile_width
        y2 = y1 + tile_height

        self.puzzle_canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            outline="blue",
            width=4
        )

    def draw_correct_ticks(self):
        """Draw green ticks on tiles that are correct."""

        if self.game is None:
            return

        grid_size = int(
            self.grid_size.get().split()[0]
        )

        tile_width = (
            self.puzzle_display_width / grid_size
        )

        tile_height = (
            self.puzzle_display_height / grid_size
        )

        for tile in self.tiles:
            if not self.game.is_tile_correct(tile):
                continue

            row, col = tile.current_position

            x = (
                self.puzzle_x_offset
                + col * tile_width
                + tile_width - 15
            )

            y = (
                self.puzzle_y_offset
                + row * tile_height
                + 15
            )

            self.puzzle_canvas.create_text(
                x,
                y,
                text="✓",
                fill="green",
                font=("Arial", 18, "bold")
            )

    def show_hint(self):
        """Show a hint for one incorrect tile."""

        if self.game is None:
            messagebox.showwarning(
                "Hint",
                "Please load an image first."
            )
            return

        if self.game.game_finished:
            return

        tile = self.game.get_hint()

        if tile is None:
            if self.game.hints_remaining() == 0:
                messagebox.showinfo(
                    "Hint",
                    "You have used all 3 hints."
                )
            return

        self.hint_tile = tile

        self.display_original()
        self.display_puzzle()
        self.update_status()

    def draw_puzzle_hint(self):
        """Draw a blue circle on the hinted puzzle tile."""

        if self.hint_tile is None:
            return

        grid_size = int(
            self.grid_size.get().split()[0]
        )

        row, col = (
            self.hint_tile.current_position
        )

        tile_width = (
            self.puzzle_display_width / grid_size
        )

        tile_height = (
            self.puzzle_display_height / grid_size
        )

        centre_x = (
            self.puzzle_x_offset
            + col * tile_width
            + tile_width / 2
        )

        centre_y = (
            self.puzzle_y_offset
            + row * tile_height
            + tile_height / 2
        )

        radius = min(
            tile_width,
            tile_height
        ) * 0.18

        self.puzzle_canvas.create_oval(
            centre_x - radius,
            centre_y - radius,
            centre_x + radius,
            centre_y + radius,
            outline="blue",
            width=4
        )

    def draw_original_hint(self):
        """Show the hinted tile's correct position on the original."""

        if self.hint_tile is None:
            return

        grid_size = int(
            self.grid_size.get().split()[0]
        )

        row, col = (
            self.hint_tile.original_position
        )

        tile_width = (
            self.original_display_width / grid_size
        )

        tile_height = (
            self.original_display_height / grid_size
        )

        centre_x = (
            self.original_x_offset
            + col * tile_width
            + tile_width / 2
        )

        centre_y = (
            self.original_y_offset
            + row * tile_height
            + tile_height / 2
        )

        radius = min(
            tile_width,
            tile_height
        ) * 0.18

        self.original_canvas.create_oval(
            centre_x - radius,
            centre_y - radius,
            centre_x + radius,
            centre_y + radius,
            outline="blue",
            width=4
        )

    def solve_puzzle(self):
        """Immediately solve the puzzle."""

        if self.game is None:
            messagebox.showwarning(
                "Solve",
                "Please load an image first."
            )
            return

        # Restore each tile's orientation and position.
        # This avoids the read-only flipped property conflict
        # between game_logic.py and image_processor.py.
        for tile in self.tiles:

            if tile.flipped_h:
                tile.flip_horizontal()

            if tile.flipped_v:
                tile.flip_vertical()

            while tile.rotation % 360 != 0:
                tile.rotate_90()

            tile.current_position = (
                tile.original_position
            )

        self.game.moves = 0
        self.game.game_finished = True

        self.selected_tile = None
        self.hint_tile = None

        self.display_original()
        self.display_puzzle()
        self.update_status()

    def update_status(self):
        """Update moves, incorrect tiles and hints."""

        if self.game is None:
            return

        self.moves_label.config(
            text=f"Moves: {self.game.moves}"
        )

        self.incorrect_label.config(
            text=(
                "Tiles Incorrect: "
                f"{self.game.count_incorrect_tiles()}"
            )
        )

        self.hints_label.config(
            text=(
                "Hints Remaining: "
                f"{self.game.hints_remaining()}"
            )
        )


def main():
    root = tk.Tk()
    app = PuzzleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
