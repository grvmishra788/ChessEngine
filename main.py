import pygame as p
import ChessEngine
from Constants import WIDTH, HEIGHT, DIMS, SQ_SIZE, MAX_FPS

IMAGES = {}


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def draw_game_state(screen, curr_state):
    draw_board(screen)
    draw_pieces(screen, curr_state.board)


def draw_board(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMS):
        for c in range(DIMS):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMS):
        for c in range(DIMS):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    currState = ChessEngine.GameState()
    validMoves = currState.get_all_valid_moves()
    moveMade = False
    load_images()
    running = True
    squareSelected = ()
    playerClicks = []
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # handle mouse clicks
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if squareSelected == (row, col):  # user clicked the same square => UNDO
                    squareSelected = ()
                    playerClicks = []
                else:
                    squareSelected = (row, col)
                    playerClicks.append(squareSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], currState.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                moveMade = True
                                currState.make_move(validMoves[i])
                                # reset
                                squareSelected = ()
                                playerClicks = []
                        if not moveMade:
                            # set the first square as the last selected square
                            playerClicks = [squareSelected]
            # handle key presses
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # if 'z' is pressed
                    currState.undo_move()
                    moveMade = True

        if moveMade:
            validMoves = currState.get_all_valid_moves()
            moveMade = False

        clock.tick(MAX_FPS)
        draw_game_state(screen, currState)
        p.display.flip()


if __name__ == "__main__":
    main()
