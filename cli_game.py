from game_engine import SuperBoard, Strategy, X, O
import sys

def get_player_move(sb: SuperBoard):
    """Ask the human player for a valid move."""
    while True:
        try:
            if sb.next_board is None:
                board = int(input("Enter board index (0–8): "))
            else:
                board = sb.next_board
                print(f"You must play in board #{board}.")

            pos = int(input("Enter position (0–8): "))

            if not (0 <= board <= 8 and 0 <= pos <= 8):
                print("Please enter numbers between 0 and 8.")
                continue
            if sb.grid[board].grid[pos] is not None:
                print("That spot is already taken.")
                continue
            return board, pos
        except ValueError:
            print("Invalid input. Please enter integers between 0–8.")


def main():
    print("=== Super Tic Tac Toe ===")
    print("You are 'O'. The AI is 'X'.")
    print("Boards and positions are indexed 0–8 like a 3×3 grid.")
    print("-" * 50)

    sb = SuperBoard()
    ai_player = X

    while not sb.winner:
        print(sb)
        print()

        if sb.current_player == O:
            b_idx, pos = get_player_move(sb)
        else:
            print("AI thinking...")
            b_idx, pos = Strategy.minimax_pick(sb, depth=4, ai_player=ai_player)
            print(f"AI plays on board {b_idx}, position {pos}.\n")

        try:
            sb.make_move(pos, board=b_idx)
        except ValueError as e:
            print("Error:", e)
            continue

        if sb.winner:
            print(sb)
            print(f"🎉 Game Over! Winner: {sb.winner}")
            break

        if all(b.winner or all(c in (X, O) for c in b.grid) for b in sb.grid):
            print(sb)
            print("It's a draw!")
            break

    print("\nGame history:")
    print(sb.history_df())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nGame exited.")
