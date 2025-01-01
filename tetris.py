import pygame
import sys
import random
import numpy as np

# -------------------- CONFIG -------------------- #
BLOCK_SIZE = 30               # Size of each Tetris cell
BOARD_WIDTH = 10              # Columns
BOARD_HEIGHT = 20             # Rows
WINDOW_WIDTH = 500            # Pixel width of the window
WINDOW_HEIGHT = BOARD_HEIGHT * BLOCK_SIZE

BOARD_ORIGIN_X = 0
BOARD_ORIGIN_Y = 0

FPS = 60

# Gravity intervals (in frames)
NORMAL_DROP_INTERVAL = 48     # Move down every 48 frames (level 0)
SOFT_DROP_INTERVAL = 5        # Move down every 5 frames if Down key is held

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)

# Tetris shape definitions
SHAPES = {
    "I": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(0, 0), (1, 0), (2, 0), (1, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "J": [(0, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(2, 0), (0, 1), (1, 1), (2, 1)],
}

# Classic Tetris shape colors
SHAPE_COLORS = {
    "I": (0, 255, 255),     # Cyan
    "O": (255, 255, 0),     # Yellow
    "T": (128, 0, 128),     # Purple
    "S": (0, 255, 0),       # Green
    "Z": (255, 0, 0),       # Red
    "J": (0, 0, 255),       # Blue
    "L": (255, 165, 0),     # Orange
}

# Piece-specific pivot dictionary (classic approach).
# Each shape rotates around this pivot in local coords.
PIECE_PIVOTS = {
    "I": (1.5, 0.5),
    "O": (0.5, 0.5),
    "T": (1.0, 1.0),
    "S": (1.0, 1.0),
    "Z": (1.0, 1.0),
    "J": (1.0, 1.0),
    "L": (1.0, 1.0),
}


# -------------------- 3D BLOCK RENDERING -------------------- #
def lighten_color(rgb, amount=0.3):
    """Lighten an (r, g, b) color by a factor 0.0..1.0."""
    r, g, b = rgb
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return (r, g, b)

def darken_color(rgb, amount=0.3):
    """Darken an (r, g, b) color by a factor 0.0..1.0."""
    r, g, b = rgb
    r = max(0, int(r - r * amount))
    g = max(0, int(g - g * amount))
    b = max(0, int(b - b * amount))
    return (r, g, b)

def draw_3d_block(surface, base_color, x, y, size):
    """
    Draw a Tetris cell at (x, y) with dimension `size`,
    using highlight/shadow for a 3D effect.
    """
    # 1. Fill the main block
    pygame.draw.rect(surface, base_color, (x, y, size, size))

    # 2. Generate highlight & shadow colors
    highlight = lighten_color(base_color, 0.4)
    shadow = darken_color(base_color, 0.4)
    edge_thick = 3

    # 3. Draw highlight on top & left
    pygame.draw.rect(surface, highlight, (x, y, size, edge_thick))        # top
    pygame.draw.rect(surface, highlight, (x, y, edge_thick, size))        # left

    # 4. Draw shadow on bottom & right
    pygame.draw.rect(surface, shadow, (x, y + size - edge_thick, size, edge_thick))     # bottom
    pygame.draw.rect(surface, shadow, (x + size - edge_thick, y, edge_thick, size))     # right


# -------------------- SOUND: BEEPS -------------------- #
def generate_beep(freq=440, duration=0.2, volume=1.0, sample_rate=44100):
    """
    Generate a simple sine-wave beep of `freq` Hz, lasting `duration` seconds.
    Return it as a Pygame Sound object.
    """
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    waveform = (volume * np.sin(2.0 * np.pi * freq * t)).astype(np.float32)
    waveform_int16 = (waveform * 32767).astype(np.int16).tobytes()
    return pygame.mixer.Sound(buffer=waveform_int16)


# -------------------- MAIN TETRIS CLASS -------------------- #
class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tetris - Classic")

        # For held-key movement
        pygame.key.set_repeat(200, 50)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Board: 2D array [BOARD_HEIGHT][BOARD_WIDTH], storing None or (r,g,b).
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

        # Current & next piece
        self.current_shape, self.current_blocks = self.generate_piece()
        self.next_shape, self.next_blocks = self.generate_piece()

        self.current_color = SHAPE_COLORS[self.current_shape]
        self.next_color = SHAPE_COLORS[self.next_shape]

        # Start near top-middle
        self.piece_x = BOARD_WIDTH // 2 - 2
        self.piece_y = 0

        # Score & lines
        self.score = 0
        self.lines_cleared_total = 0

        # Level
        self.level = 0

        # Soft drop
        self.soft_drop_active = False

        # Frame-based drop
        self.frame_count = 0
        self.drop_interval = NORMAL_DROP_INTERVAL

        # Sounds
        pygame.mixer.init()
        self.lock_beep = generate_beep(freq=300, duration=0.1, volume=0.5)
        self.line_clear_beep = generate_beep(freq=600, duration=0.15, volume=0.5)

        self.running = True
        self.main_loop()

    def generate_piece(self):
        """Pick a random shape, return (shape_key, list_of_offsets)."""
        shape_key = random.choice(list(SHAPES.keys()))
        return shape_key, SHAPES[shape_key][:]

    def main_loop(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Process user input (key presses)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not self.check_collision(self.piece_x - 1, self.piece_y, self.current_blocks):
                        self.piece_x -= 1

                elif event.key == pygame.K_RIGHT:
                    if not self.check_collision(self.piece_x + 1, self.piece_y, self.current_blocks):
                        self.piece_x += 1

                elif event.key == pygame.K_UP:
                    # Rotate piece around its classic pivot
                    rotated = self.rotate_piece_pivot(self.current_shape, self.current_blocks)
                    if not self.check_collision(self.piece_x, self.piece_y, rotated):
                        self.current_blocks = rotated

                elif event.key == pygame.K_DOWN:
                    # Activate soft drop
                    self.soft_drop_active = True
                    self.drop_interval = SOFT_DROP_INTERVAL

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.soft_drop_active = False
                    self.drop_interval = NORMAL_DROP_INTERVAL

    def update(self):
        """Update the game state each frame."""
        self.frame_count += 1
        if self.frame_count >= self.drop_interval:
            self.frame_count = 0

            # Move piece down 1 if no collision
            if not self.check_collision(self.piece_x, self.piece_y + 1, self.current_blocks):
                self.piece_y += 1
            else:
                # Lock piece in place
                self.lock_piece()
                # Check for completed lines
                rows_cleared = self.check_complete_lines()
                if rows_cleared:
                    self.flash_and_remove_lines(rows_cleared)

                # Spawn next piece
                self.current_shape = self.next_shape
                self.current_blocks = self.next_blocks
                self.current_color = self.next_color
                self.piece_x = BOARD_WIDTH // 2 - 2
                self.piece_y = 0

                # Generate a new "next" piece
                self.next_shape, self.next_blocks = self.generate_piece()
                self.next_color = SHAPE_COLORS[self.next_shape]

                # Game over check
                if self.check_collision(self.piece_x, self.piece_y, self.current_blocks):
                    self.running = False

    def check_collision(self, px, py, blocks):
        """
        Return True if placing shape 'blocks' at (px, py) collides with
        the board or goes out of the valid region. We allow y<0 so a piece
        can start partly above the board or rotate above it.
        """
        for (x_off, y_off) in blocks:
            board_x = px + x_off
            board_y = py + y_off
            # Horizontal out-of-bounds
            if board_x < 0 or board_x >= BOARD_WIDTH:
                return True
            # Bottom boundary
            if board_y >= BOARD_HEIGHT:
                return True
            # Occupied cell
            if 0 <= board_y < BOARD_HEIGHT:
                if self.board[board_y][board_x] is not None:
                    return True
        return False

    def rotate_piece_pivot(self, shape_key, blocks):
        """
        Rotate 90° clockwise around a piece-specific pivot from PIECE_PIVOTS.
        1) Translate blocks so pivot -> (0,0)
        2) (x,y)->(y,-x)
        3) Translate back
        4) Round to int
        """
        pivot_x, pivot_y = PIECE_PIVOTS[shape_key]
        rotated = []
        for (x, y) in blocks:
            tx = x - pivot_x
            ty = y - pivot_y
            rx = ty
            ry = -tx
            fx = rx + pivot_x
            fy = ry + pivot_y
            rotated.append((int(round(fx)), int(round(fy))))
        return rotated

    def lock_piece(self):
        """Lock the current piece into the board, play the lock beep."""
        if self.lock_beep:
            self.lock_beep.play()

        for (x_off, y_off) in self.current_blocks:
            bx = self.piece_x + x_off
            by = self.piece_y + y_off
            if 0 <= by < BOARD_HEIGHT:
                self.board[by][bx] = self.current_color

    def check_complete_lines(self):
        """Find all fully-filled rows and return them as a list."""
        completed = []
        for row_idx in range(BOARD_HEIGHT):
            if all(self.board[row_idx][col] is not None for col in range(BOARD_WIDTH)):
                completed.append(row_idx)
        return completed

    def flash_and_remove_lines(self, rows):
        """
        Flash the completed lines, then remove them. Also update score,
        total lines, level, etc.
        """
        if self.line_clear_beep:
            self.line_clear_beep.play()

        lines_removed = len(rows)
        self.score += lines_removed * 100
        # Update total lines cleared
        self.lines_cleared_total += lines_removed

        # Check if we level up
        self.update_level()

        # Flash lines a couple times
        flash_times = 2
        flash_delay = 150  # milliseconds

        for _ in range(flash_times):
            # Turn the line white
            self.draw_completed_lines(rows, WHITE)
            pygame.display.flip()
            pygame.time.wait(flash_delay)

            # Revert to original
            self.draw_completed_lines(rows, None)
            pygame.display.flip()
            pygame.time.wait(flash_delay)

        # Remove lines from the board
        for row_idx in sorted(rows):
            del self.board[row_idx]
            self.board.insert(0, [None] * BOARD_WIDTH)

    def draw_completed_lines(self, rows, color_override):
        """Temporarily override lines with `color_override`, then self.draw()."""
        saved_board = [row[:] for row in self.board]

        if color_override is not None:
            for r in rows:
                for c in range(BOARD_WIDTH):
                    self.board[r][c] = color_override

        self.draw()
        self.board = saved_board

    def update_level(self):
        """
        Increase level every 10 lines. Adjust drop speed accordingly.
        """
        new_level = self.lines_cleared_total // 10
        if new_level > self.level:
            self.level = new_level
            self.speed_up_game()

    def speed_up_game(self):
        """
        Decrease the drop interval to make pieces fall faster as the level increases.
        For example, reduce by 5 frames each level, down to a minimum of 1.
        """
        self.drop_interval = max(1, NORMAL_DROP_INTERVAL - 5 * self.level)

    def draw(self):
        """Render the board, the current piece, the next piece, and the HUD info."""
        self.screen.fill(WHITE)

        # 1) Draw the board
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                cell_color = self.board[y][x]
                rx = BOARD_ORIGIN_X + x * BLOCK_SIZE
                ry = BOARD_ORIGIN_Y + y * BLOCK_SIZE

                if cell_color is None:
                    # Empty cell: just draw a thin grid
                    pygame.draw.rect(
                        self.screen, LIGHT_GRAY,
                        (rx, ry, BLOCK_SIZE, BLOCK_SIZE),
                        1
                    )
                else:
                    draw_3d_block(self.screen, cell_color, rx, ry, BLOCK_SIZE)

        # 2) Draw the current falling piece (if visible)
        for (x_off, y_off) in self.current_blocks:
            rx = BOARD_ORIGIN_X + (self.piece_x + x_off) * BLOCK_SIZE
            ry = BOARD_ORIGIN_Y + (self.piece_y + y_off) * BLOCK_SIZE
            if ry < BOARD_HEIGHT * BLOCK_SIZE:
                draw_3d_block(self.screen, self.current_color, rx, ry, BLOCK_SIZE)

        # 3) Draw the "Next piece" preview
        label_text = self.font.render("Next:", True, BLACK)
        self.screen.blit(label_text, (320, 50))
        self.draw_next_piece()

        # 4) Draw the score
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (320, 200))

        # 5) Draw the current level
        level_text = self.font.render(f"Level: {self.level}", True, BLACK)
        self.screen.blit(level_text, (320, 240))

        pygame.display.flip()

    def draw_next_piece(self):
        """Draw the next piece in a small preview area at (320, 100)."""
        PREVIEW_BLOCK_SIZE = 20
        x_base = 320
        y_base = 100

        xs = [b[0] for b in self.next_blocks]
        ys = [b[1] for b in self.next_blocks]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width = max_x - min_x + 1
        height = max_y - min_y + 1

        offset_x = (4 - width) // 2
        offset_y = (4 - height) // 2

        for (x_off, y_off) in self.next_blocks:
            nx = x_off - min_x + offset_x
            ny = y_off - min_y + offset_y
            draw_x = x_base + nx * PREVIEW_BLOCK_SIZE
            draw_y = y_base + ny * PREVIEW_BLOCK_SIZE
            draw_3d_block(self.screen, self.next_color, draw_x, draw_y, PREVIEW_BLOCK_SIZE)


if __name__ == "__main__":
    Tetris()
