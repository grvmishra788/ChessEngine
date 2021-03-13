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
        self.whiteKingLoc = (7, 4)
        self.blackKingLoc = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []

    # function to execute a Move (doesn't work for castling, en passant, and pawn promotion)
    def make_move(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        # update the king's location
        if move.pieceMoved == "wK":
            self.whiteKingLoc = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLoc = (move.endRow, move.endCol)

    # function to undo the last move
    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.whiteToMove = not self.whiteToMove
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # update the king's location
            if move.pieceMoved == "wK":
                self.whiteKingLoc = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLoc = (move.startRow, move.startCol)

    def get_all_valid_moves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.get_pins_and_checks()
        if self.whiteToMove:
            kingRow = self.whiteKingLoc[0]
            kingCol = self.whiteKingLoc[1]
        else:
            kingRow = self.blackKingLoc[0]
            kingCol = self.blackKingLoc[1]
        if self.inCheck:
            if len(self.checks) == 1:  # single check
                moves = self.get_all_possible_moves()
                # to block this check, do - 1. capture the piece checking, 2. block the check, 3. move the king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking == 'N':  # if knight is checking
                    # it must be captured
                    validSquares = (checkRow, checkCol)
                else:
                    dx = check[2]
                    dy = check[3]
                    r = kingRow + dx
                    c = kingCol + dy
                    while GameState.check_bounds(r, c):
                        validSquares.append((r, c))
                        if r == checkRow and c == checkCol:
                            break
                        r += dx
                        c += dy
                # get rid of extra moves
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':  # block or capture move
                        # if move doesn't block or capture piece
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                return self.get_king_moves(kingRow, kingCol, moves)

        else:
            moves = self.get_all_possible_moves()
        return moves

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
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            # 1 square pawn advance
            if self.board[r - 1][c] == "--":
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    # 2 square pawn advance
                    if r == 6 and self.board[r - 2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            # left capture
            if c - 1 >= 0 and self.board[r - 1][c - 1][0] == 'b':
                if not piece_pinned or pin_direction == (-1, -1):
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            # right capture
            if c + 1 < DIMS and self.board[r - 1][c + 1][0] == 'b':
                if not piece_pinned or pin_direction == (-1, 1):
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else:
            # 1 square pawn advance
            if self.board[r + 1][c] == "--":
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    # 2 square pawn advance
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            # left capture
            if c - 1 >= 0 and self.board[r + 1][c - 1][0] == 'w':
                if not piece_pinned or pin_direction == (1, -1):
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            # right capture
            if c + 1 < DIMS and self.board[r + 1][c + 1][0] == 'w':
                if not piece_pinned or pin_direction == (1, 1):
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                # can't remove queen from pin on rook moves, only remove it on bishop moves
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
                
        opposition = 'b' if self.whiteToMove else 'w'
        for dx, dy in FOUR_WAY_DIRS:
            newRow = r + dx
            newCol = c + dy

            # move without capture
            while GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol] == "--":
                if not piece_pinned or pin_direction == (dx, dy) or pin_direction == (-dx, -dy):
                    moves.append(Move((r, c), (newRow, newCol), self.board))
                    newRow = newRow + dx
                    newCol = newCol + dy

            # move with capture
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol][0] == opposition:
                if not piece_pinned or pin_direction == (dx, dy) or pin_direction == (-dx, -dy):
                    moves.append(Move((r, c), (newRow, newCol), self.board))

    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break

        ally = 'w' if self.whiteToMove else 'b'
        for dx, dy in KNIGHT_DIRS:
            newRow = r + dx
            newCol = c + dy

            # move to empty square or with capture
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol][0] != ally:
                if not piece_pinned:
                    moves.append(Move((r, c), (newRow, newCol), self.board))

    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        opposition = 'b' if self.whiteToMove else 'w'
        for dx, dy in DIAGONAL_DIRS:
            newRow = r + dx
            newCol = c + dy

            # move without capture
            while GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol] == "--":
                if not piece_pinned or pin_direction == (dx, dy) or pin_direction == (-dx, -dy):
                    moves.append(Move((r, c), (newRow, newCol), self.board))
                    newRow = newRow + dx
                    newCol = newCol + dy

            # move with capture
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol][0] == opposition:
                if not piece_pinned or pin_direction == (dx, dy) or pin_direction == (-dx, -dy):
                    moves.append(Move((r, c), (newRow, newCol), self.board))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        ally = 'w' if self.whiteToMove else 'b'
        for dx, dy in FOUR_WAY_DIRS + DIAGONAL_DIRS:
            newRow = r + dx
            newCol = c + dy

            # move to empty square or with capture 
            if GameState.check_bounds(newRow, newCol) and self.board[newRow][newCol][0] != ally:
                # place king on end square and check for checks
                if ally == "w":
                    self.whiteKingLoc = (newRow, newCol)
                else:
                    self.blackKingLoc = (newRow, newCol)
                in_check, pins, checks = self.get_pins_and_checks()
                if not in_check:
                    moves.append(Move((r, c), (newRow, newCol), self.board))
                # place king back on original location
                if ally == "w":
                    self.whiteKingLoc = (r, c)
                else:
                    self.blackKingLoc = (r, c)

    def get_pins_and_checks(self):
        pins = []
        checks = []
        inCheck = False
        if self.whiteToMove:
            ally = "w"
            opposition = "b"
            r = self.whiteKingLoc[0]
            c = self.whiteKingLoc[1]
        else:
            ally = "b"
            opposition = "w"
            r = self.blackKingLoc[0]
            c = self.blackKingLoc[1]

        # check radially outwards from king for pins and checks
        index = -1
        for dx, dy in FOUR_WAY_DIRS + DIAGONAL_DIRS:
            index += 1
            newRow = r + dx
            newCol = c + dy
            possiblePin = ()
            distance = 0
            while GameState.check_bounds(newRow, newCol):
                distance += 1
                piece = self.board[newRow][newCol]
                if piece[0] == ally and piece[1] != 'K':
                    # a piece could be a pin only if it is the first ally piece between king and attacker
                    if possiblePin == ():
                        possiblePin = (newRow, newCol, dx, dy)
                    else:
                        break
                elif piece[0] == opposition:
                    pieceType = piece[1]
                    # 5 possibilities - 1. orthogonally away from king and the piece is a rook 2. diagonally away from
                    # king and the piece is a bishop 3. diagonally 1 square away from king and the piece is a pawn 4.
                    # any direction and the piece is a queen 5. any direction 1 square away and the piece is a king (
                    # prevents king's movement to a square controlled by opposite king )
                    if (0 <= index <= 3 and pieceType == 'R') or \
                            (4 <= index <= 7 and pieceType == 'B') or \
                            (distance == 1 and pieceType == 'p' and ((opposition == 'w' and 6 <= index <= 7) or (
                                    opposition == 'b' and 4 <= index <= 5))) or \
                            (pieceType == 'Q') or \
                            (distance == 1 and pieceType == 'K'):
                        if possiblePin == ():  # if no piece blocking the opposition piece
                            # it is a check
                            inCheck = True
                            checks.append((newRow, newCol, dx, dy))
                        else:
                            # it is a pin
                            pins.append(possiblePin)

                        break  # whether it is a check or a pin, you do not need to look more in the same direction
                    else:
                        # enemy piece but not applying pin or check
                        break
                newRow = newRow + dx
                newCol = newCol + dy
        # handle knight checks
        for dx, dy in KNIGHT_DIRS:
            newRow = r + dx
            newCol = c + dy
            if GameState.check_bounds(newRow, newCol):
                piece = self.board[newRow][newCol]
                if piece[0] == opposition and piece[1] == 'N':
                    inCheck = True
                    checks.append((newRow, newCol, dx, dy))
        return inCheck, pins, checks

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
