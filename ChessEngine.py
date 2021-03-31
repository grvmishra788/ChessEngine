from Constants import DIMS, FOUR_WAY_DIRS, DIAGONAL_DIRS, KNIGHT_DIRS, COLS_TO_FILES, ROWS_TO_RANKS


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
        self.stateRepetitionCounts = {}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLoc = (7, 4)
        self.blackKingLoc = (0, 4)
        self.inCheck = False
        self.checkmate = False
        self.stalemate = False
        self.repetition = False
        self.pins = []
        self.checks = []
        self.enPassantPossible = ()
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.castlingRights = CastleRights(True, True, True, True)
        self.castlingRightsLog = [CastleRights(True, True, True, True)]

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
        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        # en passant
        if move.isEnPassant:
            self.board[move.startRow][move.endCol] = "--"  # capture the opposition pawn located at (startRow, endCol)
        # castle
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side castle
                # move the rook - which is in col endCol + 1
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            elif move.startCol - move.endCol == 2:  # queen side castle
                # move the rook - which is in col endCol - 2
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        # update enPassantPossible
        if move.pieceMoved[1] == 'p' and abs(move.endRow - move.startRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.endCol)
        else:
            self.enPassantPossible = ()
        self.enPassantPossibleLog.append(self.enPassantPossible)
        # update repetition count
        boardString = str(self)
        if boardString in self.stateRepetitionCounts.keys():
            self.stateRepetitionCounts[boardString] += 1
        else:
            self.stateRepetitionCounts[boardString] = 1
        if self.stateRepetitionCounts[boardString] == 3:
            self.repetition = True
        # update castling rights
        self.update_castle_rights(move)

    # function to undo the last move
    def undo_move(self):
        if len(self.moveLog) != 0:
            # update repetition count
            self.stateRepetitionCounts[str(self)] -= 1
            self.repetition = False
            # update board state
            move = self.moveLog.pop()
            self.whiteToMove = not self.whiteToMove
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # update the king's location
            if move.pieceMoved == "wK":
                self.whiteKingLoc = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLoc = (move.startRow, move.startCol)
            # undo en passant
            if move.isEnPassant:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]

            # undo castle
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side castle
                    # move the rook - which is in col endCol + 1
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                elif move.startCol - move.endCol == 2:  # queen side castle
                    # move the rook - which is in col endCol - 2
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
            # update castling rights
            self.undo_update_castle_rights()

            # undo checkmate or stalemate flags
            self.checkmate = False
            self.stalemate = False

    def update_castle_rights(self, move):
        # update - when it is a king or a rook move
        if move.pieceMoved == 'wK':
            self.castlingRights.wks = False
            self.castlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.castlingRights.bks = False
            self.castlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.castlingRights.wqs = False
                elif move.startCol == 7:  # right rook
                    self.castlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.castlingRights.bqs = False
                elif move.startCol == 7:  # right rook
                    self.castlingRights.bks = False
        # update - when a rook is captured
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:  # left rook
                    self.castlingRights.wqs = False
                elif move.endCol == 7:  # right rook
                    self.castlingRights.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:  # left rook
                    self.castlingRights.bqs = False
                elif move.endCol == 7:  # right rook
                    self.castlingRights.bks = False

        self.castlingRightsLog.append(CastleRights(self.castlingRights.wks, self.castlingRights.bks,
                                                   self.castlingRights.wqs, self.castlingRights.bqs))

    def undo_update_castle_rights(self):
        self.castlingRightsLog.pop()
        self.castlingRights = self.castlingRightsLog[-1]

    def get_all_valid_moves(self):
        # init temp vars to make sure we do not modify enPassantPossible or castleRights unknowingly
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.castlingRights.wks, self.castlingRights.bks, self.castlingRights.wqs,
                                        self.castlingRights.bqs)
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
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':  # block or capture move
                        # if move doesn't block or capture piece
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:  # >=2 checks - king has to move
                self.get_king_moves(kingRow, kingCol, moves)

        else:  # not in check
            moves = self.get_all_possible_moves()
            if self.whiteToMove:
                self.get_castle_moves(self.whiteKingLoc[0], self.whiteKingLoc[1], moves)
            else:
                self.get_castle_moves(self.blackKingLoc[0], self.blackKingLoc[1], moves)

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enPassantPossible = tempEnPassantPossible
        self.castlingRights = tempCastleRights
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

    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.whiteKingLoc[0], self.whiteKingLoc[1])
        else:
            return self.square_under_attack(self.blackKingLoc[0], self.blackKingLoc[1])

    def square_under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        opponentsMoves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove
        for move in opponentsMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

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
            if c - 1 >= 0:
                if not piece_pinned or pin_direction == (-1, -1):
                    if self.board[r - 1][c - 1][0] == 'b':
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                    elif (r - 1, c - 1) == self.enPassantPossible:
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassant=True))

            # right capture
            if c + 1 < DIMS:
                if not piece_pinned or pin_direction == (-1, 1):
                    if self.board[r - 1][c + 1][0] == 'b':
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                    elif (r - 1, c + 1) == self.enPassantPossible:
                        moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassant=True))
        else:
            # 1 square pawn advance
            if self.board[r + 1][c] == "--":
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    # 2 square pawn advance
                    if r == 1 and self.board[r + 2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            # left capture
            if c - 1 >= 0:
                if not piece_pinned or pin_direction == (1, -1):
                    if self.board[r + 1][c - 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enPassantPossible:
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassant=True))

            # right capture
            if c + 1 < DIMS:
                if not piece_pinned or pin_direction == (1, 1):
                    if self.board[r + 1][c + 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enPassantPossible:
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassant=True))

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

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return  # can't castle if king is in check
        if (self.whiteToMove and self.castlingRights.wks) or (not self.whiteToMove and self.castlingRights.bks):
            self.get_king_side_castle_moves(r, c, moves)
        if (self.whiteToMove and self.castlingRights.wqs) or (not self.whiteToMove and self.castlingRights.bqs):
            self.get_queen_side_castle_moves(r, c, moves)

    def get_king_side_castle_moves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def get_queen_side_castle_moves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))

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

    def __str__(self):
        result = ""
        for r in range(DIMS):
            for c in range(DIMS):
                result += self.board[r][c] + " "
        return result

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    def __init__(self, startSquare, endSquare, board, isEnPassant=False, isCastleMove=False):
        self.startRow = startSquare[0]
        self.startCol = startSquare[1]
        self.endRow = endSquare[0]
        self.endCol = endSquare[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
                self.pieceMoved == 'bp' and self.endRow == 7)
        # en passant
        self.isEnPassant = isEnPassant
        if self.isEnPassant:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        # castle
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    # Override the equals() method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    @staticmethod
    def get_rank_file(row, col):
        return COLS_TO_FILES[col] + ROWS_TO_RANKS[row]

    def get_chess_notation(self):
        return self.get_rank_file(self.startRow, self.startCol) + self.get_rank_file(self.endRow, self.endCol)

    def __str__(self):
        if self.isCastleMove:
            return "0-0" if self.endCol == 6 else "0-0-0"

        endSquare = self.get_rank_file(self.endRow, self.endCol)

        # pawn moves
        if self.pieceMoved[1] == "p":
            moveString = ""
            if self.pieceCaptured != "--":
                moveString += COLS_TO_FILES[self.startCol] + "x" + endSquare
            else:
                moveString += endSquare
            # pawn promotion
            if self.isPawnPromotion:
                moveString += "=Q"
            return moveString

        moveString = self.pieceMoved[1]
        if self.pieceCaptured != "--":
            moveString += "x"
        return moveString + endSquare
