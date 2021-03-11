import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMS = 8
SQ_SIZE = HEIGHT // DIMS
MAX_FPS = 15
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
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE) )


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    curr_state = ChessEngine.GameState()
    load_images()
    running = True
    squareSelected = ()
    playerClicks = []
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if squareSelected == (row,col): #user clicked the same square => UNDO
                    squareSelected = ()
                    playerClicks = []
                else:
                    squareSelected = (row, col)
                    playerClicks.append(squareSelected)
                    if len(playerClicks)==2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], curr_state.board)
                        print(move.get_chess_notation())
                        curr_state.make_move(move)
                        #reset
                        squareSelected = ()
                        playerClicks = []
        clock.tick(MAX_FPS)
        draw_game_state(screen, curr_state)
        p.display.flip()


if __name__ == "__main__":
    main()
