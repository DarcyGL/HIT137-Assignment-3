import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import cv2

from image_processor import load_and_process_image, reassemble_image
from game_logic import GameLogic


class PuzzleGUI:
    """Main graphical interface for the image puzzle game."""

    def __init__(self, root):
        self.root = root
        self.root.title("Image Puzzle Game")
        self.root.geometry("1100x700")

        # Stores the image currently being used
        self.original_image = None
        self.original_photo = None
        self.image_path = None

        # Puzzle data
        self.tiles = []
        self.game = None
        self.puzzle_photo = None

        self.create_widgets()

    def create_widgets(self):
        # Main heading
        title_label = tk.Label(
            self.root,
            text="Image Puzzle Game",
            font=("Arial", 22, "bold")
        )
        title_label.pack(pady=15)

        # Frame for controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        # Grid size selection
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

        # Load image button
        self.load_button = tk.Button(
            control_frame,
            text="Load Image",
            width=12,
            command=self.load_image
        )
        self.load_button.grid(row=0, column=2, padx=10)

        # Hint button
        self.hint_button = tk.Button(
            control_frame,
            text="Hint",
            width=10
        )
        self.hint_button.grid(row=0, column=3, padx=10)

        # Solve button
        self.solve_button = tk.Button(
            control_frame,
            text="Solve",
            width=10
        )
        self.solve_button.grid(row=0, column=4, padx=10)

        # Score information
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

        # Area containing both images
        image_frame = tk.Frame(self.root)
        image_frame.pack(
            expand=True,
            fill="both",
            padx=20,
            pady=10
        )

        # Original image side
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

        # Puzzle image side
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

        # Player instructions
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
        """Load an image and create a new scrambled puzzle."""

        file_path = filedialog.askopenfilename(
            title="Choose an Image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp"),
                ("JPEG Files", "*.jpg *.jpeg"),
                ("PNG Files", "*.png"),
                ("BMP Files", "*.bmp")
            ]
        )

        # If the player presses Cancel, do nothing
        if not file_path:
            return

        try:
            # Convert "3 x 3" into the integer 3
            grid_size = int(self.grid_size.get().split()[0])

            # Use image_processor.py to load, resize,
            # divide and scramble the image
            original, tiles = load_and_process_image(
                file_path,
                grid_size
            )

            self.image_path = file_path
            self.original_image = original
            self.tiles = tiles

            # Start or reset the game logic
            if self.game is None:
                self.game = GameLogic(self.tiles)
            else:
                self.game.reset_game(self.tiles)

            # Display original and puzzle images
            self.display_original(original)
            self.display_puzzle()

            # Update score information
            self.update_status()

        except Exception as error:
            messagebox.showerror(
                "Image Error",
                "The image could not be loaded.\n\n"
                + str(error)
            )

    def display_original(self, image):
        """Display the original processed image."""

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        pil_image = Image.fromarray(rgb_image)
        pil_image.thumbnail((400, 400))

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

    def display_puzzle(self):
        """Reassemble and display the current puzzle."""

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