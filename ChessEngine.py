from Constants import DIMS, FOUR_WAY_DIRS, DIAGONAL_DIRS, KNIGHT_DIRS


class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {
            'p': self.get_pawn_moves,
            'R': self.get_rook_moves,
            'N': self.get_knight_moves,
            'B': self.get_bishop_moves,
            'Q': self.get_queen_moves,
            'K': self.get_king_moves
        }
        self.whiteToMove = True
        self.moveLog = []

    # function to execute a Move (doesn't work for castling, en passant, and pawn promotion)
    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove

    # function to undo the last move
    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.whiteToMove = not self.whiteToMove
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured

    def get_all_valid_moves(self):
        return self.get_all_possible_moves()

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # returns 'w' or 'b'
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.whiteToMove:
            # 1 square pawn advance
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                # 2 square pawn advance
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            # left capture
            if c - 1 >= 0 and self.board[r - 1][c - 1][0] == 'b':
                moves.append(Move((r, c), (r - 1, c - 1), self.board))
            # right capture
            if c + 1 < DIMS and self.board[r - 1][c + 1][0] == 'b':
                moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:
            # 1 square pawn advance
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                # 2 square pawn advance
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # left capture
            if c - 1 >= 0 and self.board[r + 1][c - 1][0] == 'w':
                moves.append(Move((r, c), (r + 1, c - 1), self.board))
            # right capture
            if c + 1 < DIMS and self.board[r + 1][c + 1][0] == 'w':
                moves.append(Move((r, c), (r + 1, c + 1), self.board))

    def get_rook_moves(self, r, c, moves):
        opposition = 'b' if self.whiteToMove else 'w'
        for dx, dy in FOUR_WAY_DIRS:
            newRow = r + dx
            newCol = c + dy

            # move without capture
            while GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol] == "--":
                moves.append(Move((r, c), (newRow, newCol), self.board))
                newRow = newRow + dx
                newCol = newCol + dy

            # move with capture
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol][0] == opposition:
                moves.append(Move((r, c), (newRow, newCol), self.board))

    def get_knight_moves(self, r, c, moves):
        opposition = 'b' if self.whiteToMove else 'w'
        for dx, dy in KNIGHT_DIRS:
            newRow = r + dx
            newCol = c + dy

            # move without capture
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol] == "--":
                moves.append(Move((r, c), (newRow, newCol), self.board))

            # move with capture
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol][0] == opposition:
                moves.append(Move((r, c), (newRow, newCol), self.board))

    def get_bishop_moves(self, r, c, moves):
        opposition = 'b' if self.whiteToMove else 'w'
        for dx, dy in DIAGONAL_DIRS:
            newRow = r + dx
            newCol = c + dy

            # move without capture
            while GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol] == "--":
                moves.append(Move((r, c), (newRow, newCol), self.board))
                newRow = newRow + dx
                newCol = newCol + dy

            # move with capture
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol][0] == opposition:
                moves.append(Move((r, c), (newRow, newCol), self.board))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        opposition = 'b' if self.whiteToMove else 'w'
        for dx, dy in FOUR_WAY_DIRS + DIAGONAL_DIRS:
            newRow = r + dx
            newCol = c + dy

            # move without capture
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol] == "--":
                moves.append(Move((r, c), (newRow, newCol), self.board))

            # move with capture
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol][0] == opposition:
                moves.append(Move((r, c), (newRow, newCol), self.board))

    @staticmethod
    def check_bounds(r, c):
        return 0 <= r < DIMS and 0 <= c < DIMS


class Move:
    # maps for move notation
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {value: key for key, value in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {value: key for key, value in files_to_cols.items()}

    def __init__(self, startSquare, endSquare, board):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Override the equals() method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)
