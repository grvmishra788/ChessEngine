BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = BOARD_WIDTH//2
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMS = 8
SQ_SIZE = BOARD_HEIGHT // DIMS
MAX_FPS = 15
FOUR_WAY_DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # UP, RIGHT, DOWN, LEFT
DIAGONAL_DIRS = [(-1, -1), (-1, 1), (1, 1), (1, -1)]  # TOP_LEFT, TOP_RIGHT, BOTTOM_RIGHT, BOTTOM_LEFT
KNIGHT_DIRS = [(-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, -2), (2, -1), (2, 1), (1, 2)]
COLORS = ["white", "gray"]

# maps for move notation
RANKS_TO_ROWS = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
ROWS_TO_RANKS = {value: key for key, value in RANKS_TO_ROWS.items()}
FILES_TO_COLS = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
COLS_TO_FILES = {value: key for key, value in FILES_TO_COLS.items()}
