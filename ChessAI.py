import random


def find_random_move(validMoves):
    return validMoves[random.randint(0, len(validMoves) - 1)]
