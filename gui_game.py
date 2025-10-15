import sys
import pygame
from game_engine import SuperBoard, Strategy, X, O


WIDTH, HEIGHT = 720, 720
FPS = 30

BACKGROUND = (28, 28, 28)
LINE_COLOR = (200, 200, 200)
X_COLOR = (200, 50, 50)
O_COLOR = (50, 200, 50)


def draw_board(screen, sb: SuperBoard, font):
    screen.fill(BACKGROUND)

    margin = 40
    board_size = min(WIDTH, HEIGHT) - margin * 2
    cell_size = board_size // 9  # because we will draw 9x9 small cells

    top_left_x = (WIDTH - board_size) // 2
    top_left_y = (HEIGHT - board_size) // 2

    # draw small grid (9x9)
    for i in range(10):
        # vertical
        x = top_left_x + i * cell_size
        pygame.draw.line(screen, LINE_COLOR, (x, top_left_y), (x, top_left_y + board_size), 1)
        # horizontal
        y = top_left_y + i * cell_size
        pygame.draw.line(screen, LINE_COLOR, (top_left_x, y), (top_left_x + board_size, y), 1)

    # draw thicker lines to separate 3x3 super-boards
    for i in range(4):
        x = top_left_x + i * 3 * cell_size
        pygame.draw.line(screen, LINE_COLOR, (x, top_left_y), (x, top_left_y + board_size), 4)
        y = top_left_y + i * 3 * cell_size
        pygame.draw.line(screen, LINE_COLOR, (top_left_x, y), (top_left_x + board_size, y), 4)

    # draw X/O in cells
    for big_idx, board in enumerate(sb.grid):
        br = big_idx // 3
        bc = big_idx % 3
        for pos, val in enumerate(board.grid):
            sr = pos // 3
            sc = pos % 3
            x = top_left_x + (bc * 3 + sc) * cell_size
            y = top_left_y + (br * 3 + sr) * cell_size
            center = (x + cell_size // 2, y + cell_size // 2)
            if val == X:
                # draw X
                off = cell_size // 3
                pygame.draw.line(screen, X_COLOR, (center[0]-off, center[1]-off), (center[0]+off, center[1]+off), 3)
                pygame.draw.line(screen, X_COLOR, (center[0]-off, center[1]+off), (center[0]+off, center[1]-off), 3)
            elif val == O:
                pygame.draw.circle(screen, O_COLOR, center, cell_size // 3, 3)

    # highlight next board if set
    if sb.next_board is not None and not sb.grid[sb.next_board].winner:
        nb = sb.next_board
        br = nb // 3
        bc = nb % 3
        x = top_left_x + (bc * 3) * cell_size
        y = top_left_y + (br * 3) * cell_size
        rect = pygame.Rect(x, y, cell_size * 3, cell_size * 3)
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        s.fill((255, 255, 0, 40))
        screen.blit(s, rect.topleft)

    # show status
    status = f"Current: {sb.current_player}"
    if sb.winner:
        status = f"Winner: {sb.winner}"
    text = font.render(status, True, LINE_COLOR)
    screen.blit(text, (10, 10))


def pos_to_board_cell(pos, margin=40):
    x, y = pos
    board_size = min(WIDTH, HEIGHT) - margin * 2
    cell_size = board_size // 9
    top_left_x = (WIDTH - board_size) // 2
    top_left_y = (HEIGHT - board_size) // 2

    if not (top_left_x <= x <= top_left_x + board_size and top_left_y <= y <= top_left_y + board_size):
        return None

    rel_x = x - top_left_x
    rel_y = y - top_left_y
    big_col = rel_x // (cell_size * 1)
    big_row = rel_y // (cell_size * 1)

    # compute indices within 9x9
    col9 = int(rel_x // cell_size)
    row9 = int(rel_y // cell_size)

    big_board_col = col9 // 3
    big_board_row = row9 // 3
    small_col = col9 % 3
    small_row = row9 % 3

    board_idx = big_board_row * 3 + big_board_col
    cell_idx = small_row * 3 + small_col
    return board_idx, cell_idx


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Super Tic-Tac-Toe")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    sb = SuperBoard()

    # choose mode: Human vs AI (default) or Human vs Human (press H)
    mode_ai = True

    running = True
    ai_thinking = False

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    sb = SuperBoard()
                elif event.key == pygame.K_h:
                    mode_ai = not mode_ai
                elif event.key == pygame.K_s:
                    # print history to console
                    print(sb.history_df())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if sb.winner:
                    continue
                board_cell = pos_to_board_cell(event.pos)
                if board_cell is None:
                    continue
                b_idx, pos_idx = board_cell
                try:
                    # if next_board is set and user clicked on other board, ignore
                    if sb.next_board is not None and b_idx != sb.next_board:
                        print(f"You must play in board {sb.next_board}")
                        continue
                    if sb.grid[b_idx].grid[pos_idx] is not None:
                        print("That spot is already taken.")
                        continue
                    # only allow human to play when current_player is O if vs AI (matches cli_game)
                    if mode_ai and sb.current_player == X:
                        # AI's turn; ignore clicks
                        continue
                    sb.make_move(pos_idx, board=b_idx)
                except Exception as e:
                    print("Error:", e)

        # AI move
        if not sb.winner and mode_ai and sb.current_player == X:
            ai_thinking = True
            pygame.display.set_caption("Super Tic-Tac-Toe - AI thinking...")
            pygame.event.pump()
            try:
                b_idx, pos_idx = Strategy.minimax_pick(sb, depth=4, ai_player=X)
                if b_idx is not None:
                    sb.make_move(pos_idx, board=b_idx)
            except Exception as e:
                print("AI Error:", e)
            ai_thinking = False
            pygame.display.set_caption("Super Tic-Tac-Toe")

        draw_board(screen, sb, font)

        # footer
        footer = f"Mode: {'AI' if mode_ai else 'Human'}   (R)eset  (H) Toggle mode  (S)how history  (Esc) Quit"
        ft = font.render(footer, True, LINE_COLOR)
        screen.blit(ft, (10, HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
