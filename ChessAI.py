import random

PIECE_SCORE = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE_SCORE = 1000
STALEMATE_SCORE = 0
MAX_DEPTH = 2


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


'''
    Helper function to make first recursive call to find_move_min_max
'''


def find_best_move_min_max(currState, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    find_move_min_max(currState, validMoves, MAX_DEPTH, currState.whiteToMove)
    return nextMove


'''
    Helper function to make first recursive call to find_move_nega_max
'''


def find_best_move_nega_max(currState, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    find_move_nega_max(currState, validMoves, MAX_DEPTH, 1 if currState.whiteToMove else -1)
    return nextMove


'''
    Helper function to make first recursive call to find_move_nega_max_alpha_beta
'''


def find_best_move_nega_max_alpha_beta(currState, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    find_move_nega_max_alpha_beta(currState, validMoves, MAX_DEPTH, -CHECKMATE_SCORE, CHECKMATE_SCORE, 1 if currState.whiteToMove else -1)
    return nextMove


'''
    Recursive function to find the best move using min max algo
'''


def find_move_min_max(currState, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return score_material(currState.board)

    if whiteToMove:
        maxScore = -CHECKMATE_SCORE
        for move in validMoves:
            currState.make_move(move)
            nextMoves = currState.get_all_valid_moves()
            score = find_move_min_max(currState, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == MAX_DEPTH:
                    nextMove = move
            currState.undo_move()
        return maxScore
    else:
        minScore = CHECKMATE_SCORE
        for move in validMoves:
            currState.make_move(move)
            nextMoves = currState.get_all_valid_moves()
            score = find_move_min_max(currState, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == MAX_DEPTH:
                    nextMove = move
            currState.undo_move()
        return minScore


'''
    Recursive function to find the best move using nega max algo
'''


def find_move_nega_max(currState, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * score_board(currState)
    maxScore = -CHECKMATE_SCORE
    for move in validMoves:
        currState.make_move(move)
        nextMoves = currState.get_all_valid_moves()
        score = - find_move_nega_max(currState, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == MAX_DEPTH:
                nextMove = move
        currState.undo_move()
    return maxScore


'''
    Recursive function to find the best move using nega max algo and alpha-beta pruning
'''


def find_move_nega_max_alpha_beta(currState, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * score_board(currState)
    maxScore = -CHECKMATE_SCORE
    for move in validMoves:
        currState.make_move(move)
        nextMoves = currState.get_all_valid_moves()
        score = - find_move_nega_max_alpha_beta(currState, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == MAX_DEPTH:
                nextMove = move
        currState.undo_move()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore


'''
Scores the current game state based on multiple factors.
(+ve score is good for white, -ve score is good for black)
'''


def score_board(currState):
    if currState.checkmate:
        if currState.whiteToMove:
            return -CHECKMATE_SCORE  # black wins
        else:
            return CHECKMATE_SCORE  # white wins
    elif currState.stalemate:
        return STALEMATE_SCORE
    else:
        score = 0
        for row in currState.board:
            for square in row:
                if square[0] == 'w':
                    score += PIECE_SCORE[square[1]]
                elif square[0] == 'b':
                    score -= PIECE_SCORE[square[1]]
        return score


'''
Scores the current game state based on only material.
'''


def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += PIECE_SCORE[square[1]]
            elif square[0] == 'b':
                score -= PIECE_SCORE[square[1]]
    return score
