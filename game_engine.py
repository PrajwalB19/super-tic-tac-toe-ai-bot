from Minimax import minimax
import random
from copy import deepcopy
import pandas as pd

X = "X"
O = "O"

WINNING_COMBINATIONS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6]
]

class Board:
    def __init__(self, current_player):
        self.grid = [None for i in range(9)]
        self.current_player = current_player
        self.winner = None

    def __str__(self):
        def cell_repr(val):
            return val if val in (X, O) else '.'

        rows = []
        for r in range(3):
            row_cells = [cell_repr(self.grid[r*3 + c]) for c in range(3)]
            rows.append(' '.join(row_cells))

        status = f"Winner: {self.winner}" if self.winner else ''
        if status:
            return '\n'.join(rows) + '\n' + status
        return '\n'.join(rows)

    def check_winner(self):
        for combo in WINNING_COMBINATIONS:
            if (self.grid[combo[0]] == self.grid[combo[1]] == self.grid[combo[2]]) and (self.grid[combo[0]] in [X, O]):
                self.winner = self.grid[combo[0]]
                return True
        return False

    def clone(self):
        """Return a deep-ish copy of this small board."""
        b = Board(current_player=self.current_player)
        b.grid = list(self.grid)
        b.winner = self.winner
        return b

class SuperBoard:
    def __init__(self):
        self.grid = [Board(current_player=X) for i in range(9)]
        self.current_player = X
        self.next_board = None
        self.winner = None
        self.history = []

    def __str__(self):
        def cell_repr(val):
            return val if val in (X, O) else '.'

        lines = []
        for big_r in range(3):
            small_rows = ['' for _ in range(3)]
            for big_c in range(3):
                board_idx = big_r * 3 + big_c
                board = self.grid[board_idx]
                winner = board.winner
                for r in range(3):
                    row_cells = [cell_repr(board.grid[r*3 + c]) for c in range(3)]
                    row_str = ' '.join(row_cells)
                    small_rows[r] += row_str
                    if big_c < 2:
                        small_rows[r] += ' | '

            for sr in small_rows:
                lines.append(sr)
            if big_r < 2:
                lines.append('-' * len(small_rows[0]))

        nb = self.next_board
        nb_str = str(nb) if nb is not None else 'None'
        status = f"Current player: {self.current_player}    Next board: {nb_str}    Global winner: {self.winner}"
        lines.append(status)

        return '\n'.join(lines)

    def make_move(self, position, board=None):
        # check for local board wins
        for b in self.grid:
            b.check_winner()  # just update the winner

        # pick the board to play in
        if board is None:
            if self.next_board is not None:
                board = self.next_board
            else:
                raise ValueError("You must specify which board to play in.")

        if self.grid[board].grid[position] is None:
            player = self.current_player
            self.grid[board].grid[position] = player
            self.next_board = position
        else:
            raise ValueError("Board position taken up!")

        self.grid[board].check_winner()

        move_num = len(self.history) + 1
        small_winner = self.grid[board].winner
        entry = {
            'move': move_num,
            'player': player,
            'board': board,
            'position': position,
            'next_board': self.next_board,
            'small_winner': small_winner,
        }
        self.history.append(entry)

        self.check_winner()
        if self.winner:
            self.history[-1]['global_winner'] = self.winner

        self.current_player = O if self.current_player == X else X

    def clone(self):
        sb = SuperBoard()
        sb.grid = [deepcopy(board) for board in deepcopy(self.grid)]
        sb.current_player = self.current_player
        sb.next_board = self.next_board
        sb.winner = self.winner
        sb.history = [h.copy() for h in self.history]
        return sb

    def history_df(self):
        df = pd.DataFrame(self.history)
        df.attrs['winner'] = self.winner
        return df

    def check_winner(self):
        owners = [b.winner for b in self.grid]
        for combo in WINNING_COMBINATIONS:
            a, b, c = combo
            if owners[a] and owners[a] == owners[b] == owners[c]:
                self.winner = owners[a]
                return True
        return False

    def is_full(self, board_index):
        b = self.grid[board_index]
        return all(cell in [X, O] for cell in b.grid)

class Strategy:
    @staticmethod
    def random_pick():
        return (random.randint(0, 8), random.randint(0, 8))

    @staticmethod
    def minimax_pick(superboard, depth=20, ai_player=X):
        maximizing = (superboard.current_player == ai_player)
        score, move = minimax(superboard, maximizing, ai_player, depth)
        return move

class File:
    @staticmethod
    def parse_board(file):
        # read lines
        if isinstance(file, str):
            with open(file, 'r', encoding='utf-8') as f:
                lines = [ln.rstrip('\n') for ln in f]
        else:
            try:
                text = file.read()
                lines = text.splitlines()
            except:
                lines = list(file)

        lines = [ln.strip() for ln in lines]

        sb = SuperBoard()

        for ln in lines:
            if ln.lower().startswith('current player'):
                parts = ln.split(':', 1)
                if len(parts) > 1:
                    val = parts[1].strip()
                    if val in (X, O):
                        sb.current_player = val
            if ln.lower().startswith('active board'):
                parts = ln.split(':', 1)
                if len(parts) > 1:
                    val = parts[1].strip()
                    if val and val.startswith('(') and ',' in val:
                        try:
                            r,c = val.strip('()').split(',')
                            r = int(r)
                            c = int(c)
                            idx = (r-1)*3 + (c-1)
                            sb.next_board = idx
                        except Exception:
                            sb.next_board = None

        i = 0
        n = len(lines)
        while i < n:
            ln = lines[i]
            if ln.startswith('(') and ',' in ln and ln.endswith(')'):
                try:
                    r,c = ln.strip('()').split(',')
                    r = int(r)
                    c = int(c)
                    board_idx = (r-1)*3 + (c-1)
                except:
                    i += 1
                    continue

                row_lines = []
                j = i+1
                while j < n and len(row_lines) < 3:
                    if lines[j] != '':
                        row_lines.append(lines[j])
                    j += 1

                if len(row_lines) == 3:
                    cells = []
                    for row in row_lines:
                        tokens = [t for t in row.split() if t != '']
                        if len(tokens) == 1 and len(tokens[0]) == 3:
                            tokens = list(tokens[0])
                        for tok in tokens:
                            if tok == 'X':
                                cells.append(X)
                            elif tok == 'O':
                                cells.append(O)
                            else:
                                cells.append(None)

                    if len(cells) == 9:
                        sb.grid[board_idx].grid = cells
                i = j
            else:
                i += 1

        for b in sb.grid:
            b.check_winner()

        sb.check_winner()

        return sb
