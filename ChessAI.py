import random

PIECE_SCORE = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE_SCORE = 1000
STALEMATE_SCORE = 0


def find_random_move(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]


def find_best_move(currState, validMoves):
    turnMultiplier = 1 if currState.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE_SCORE
    bestMove = None
    random.shuffle(validMoves)
    for move in validMoves:
        currState.make_move(move)
        opponentMoves = currState.get_all_valid_moves()
        if currState.checkmate:
            opponentMaxScore = -CHECKMATE_SCORE
        elif currState.stalemate:
            opponentMaxScore = STALEMATE_SCORE
        else:
            opponentMaxScore = -CHECKMATE_SCORE
            for opponentMove in opponentMoves:
                currState.make_move(opponentMove)
                currState.get_all_valid_moves()
                if currState.checkmate:
                    score = CHECKMATE_SCORE
                elif currState.stalemate:
                    score = STALEMATE_SCORE
                else:
                    score = -turnMultiplier * score_material(currState.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                currState.undo_move()
        if opponentMinMaxScore > opponentMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestMove = move
        currState.undo_move()
    return bestMove


def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += PIECE_SCORE[square[1]]
            elif square[0] == 'b':
                score -= PIECE_SCORE[square[1]]
    return score
