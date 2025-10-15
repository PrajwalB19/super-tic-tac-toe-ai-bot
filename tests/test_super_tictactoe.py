import pytest
from game_engine import SuperBoard, X, O

def test_initial_state():
    sb = SuperBoard()
    assert sb.current_player == X
    assert sb.winner is None
    assert all(board.winner is None for board in sb.grid)

def test_make_move():
    sb = SuperBoard()
    sb.make_move(0, board=0)
    assert sb.grid[0].grid[0] == X
    assert sb.current_player == O

def test_winner_row():
    sb = SuperBoard()
    # Simulate a win on the first mini-board
    sb.grid[0].grid = [X, X, X, None, None, None, None, None, None]
    sb.grid[0].check_winner()
    assert sb.grid[0].winner == X
