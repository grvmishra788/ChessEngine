import pygame as p
import ChessAI
import ChessEngine
from Constants import BOARD_WIDTH, BOARD_HEIGHT, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT, DIMS, SQ_SIZE, MAX_FPS, COLORS

IMAGES = {}


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def highlight_squares(screen, currState, validMoves, squareSelected):
    if squareSelected != ():
        r, c = squareSelected
        if currState.board[r][c][0] == ('w' if currState.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s1 = p.Surface((SQ_SIZE, SQ_SIZE))
            s1.set_alpha(100)
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    color = p.Color(COLORS[(r + c) % 2])
                    if currState.board[move.endRow][move.endCol] == "--":
                        s1.fill(color)
                        p.draw.circle(s1, p.Color("blue"), (SQ_SIZE // 2, SQ_SIZE // 2), 10)
                    else:
                        s1.fill(p.Color("blue"))
                        p.draw.circle(s1, color, (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 2)
                    screen.blit(s1, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def animate_move(move, screen, board, clock):
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSecond = 10
    frameCount = (abs(dR) + abs(dC)) * framesPerSecond
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from it's ending square
        color = p.Color(COLORS[(move.endRow + move.endCol) % 2])
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto the rectangle
        if move.pieceCaptured != "--":
            if move.isEnPassant:
                newEnPassantRow = move.endRow + 1 if move.pieceCaptured[0]=='b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, newEnPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def draw_game_state(screen, currState, validMoves, squareSelected, moveLogFont):
    draw_board(screen)
    highlight_squares(screen, currState, validMoves, squareSelected)
    draw_pieces(screen, currState.board)
    draw_move_log(screen, currState, moveLogFont)


def draw_board(screen):
    for r in range(DIMS):
        for c in range(DIMS):
            color = p.Color(COLORS[(r + c) % 2])
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_pieces(screen, board):
    for r in range(DIMS):
        for c in range(DIMS):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_move_log(screen, currState, font):
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = currState.moveLog
    paddingX = 5
    paddingY = 5
    rowSpace = 2
    colSpace = 4
    for i in range(len(moveLog)):
        move = moveLog[i]
        text = str((i//2+1))+". " if i % 2 == 0 else ""
        text += move.get_chess_notation()
        textObj = font.render(text, True, p.Color("white"))
        textLoc = moveLogRect.move(paddingX, paddingY)
        screen.blit(textObj, textLoc)
        if i % 2 == 1:
            paddingX = 5
            paddingY += textObj.get_height() + rowSpace
        else:
            paddingX += textObj.get_width() + colSpace


def draw_game_end_text(screen, text):
    font = p.font.SysFont("Helvetic", 32, True, False)
    textObj = font.render(text, False, p.Color("gray"))
    textLoc = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH / 2 - textObj.get_width() / 2,
                                                           BOARD_HEIGHT / 2 - textObj.get_height() / 2)
    screen.blit(textObj, textLoc)
    textObj = font.render(text, False, p.Color("black"))
    screen.blit(textObj, textLoc.move(2, 2))


def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    currState = ChessEngine.GameState()
    validMoves = currState.get_all_valid_moves()
    moveLogFont = p.font.SysFont("Times New Roman", 15, False, False)
    moveMade = False
    animate = False
    gameOver = False
    load_images()
    running = True
    squareSelected = ()
    playerClicks = []
    humanIsWhite = True  # If a human is playing white, this flag will be true, else False
    humanIsBlack = True  # If a human is playing black, this flag will be true, else False
    while running:
        humanTurn = (currState.whiteToMove and humanIsWhite) or (not currState.whiteToMove and humanIsBlack)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # handle mouse clicks
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if squareSelected == (row, col) or col >= 8:  # user clicked the same square or user clicked side panel => UNDO
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
                                    animate = True
                                    currState.make_move(validMoves[i])
                                    # reset
                                    squareSelected = ()
                                    playerClicks = []
                            if not moveMade:
                                # set the first square as the last selected square
                                playerClicks = [squareSelected]
            # handle key presses
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # if 'z' is pressed, undo move
                    currState.undo_move()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r:  # if 'r' is pressed, reset board
                    currState = ChessEngine.GameState()
                    validMoves = currState.get_all_valid_moves()
                    squareSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        if not gameOver and not humanTurn:
            AIMove = ChessAI.find_best_move_nega_max_alpha_beta(currState, validMoves)
            if AIMove is None:
                AIMove = ChessAI.find_random_move(validMoves)
            currState.make_move(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animate_move(currState.moveLog[-1], screen, currState.board, clock)
            validMoves = currState.get_all_valid_moves()
            moveMade = False

        draw_game_state(screen, currState, validMoves, squareSelected, moveLogFont)
        if currState.checkmate or currState.stalemate:
            gameOver = True
            text = "Draw by stalemate!" if currState.stalemate else "0-1 : Black wins by checkmate!" if currState.whiteToMove else "1-0 : White wins by checkmate!"
            draw_game_end_text(screen, text)
        p.display.flip()
        clock.tick(MAX_FPS)


if __name__ == "__main__":
    main()
