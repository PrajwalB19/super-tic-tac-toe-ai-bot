import math

X = "X"
O = "O"

def legal_moves(superboard):
    if superboard.next_board is not None:
        nb = superboard.next_board
        if (not superboard.grid[nb].winner) and (not superboard.is_full(nb)):
            for pos, cell in enumerate(superboard.grid[nb].grid):
                if cell is None:
                    yield (nb, pos)
            return
    for b_idx, b in enumerate(superboard.grid):
        if b.winner or superboard.is_full(b_idx):
            continue
        for pos, cell in enumerate(b.grid):
            if cell is None:
                yield (b_idx, pos)

def heuristic(superboard, ai_player=X):
    superboard.check_winner()
    if superboard.winner == ai_player:
        return 100000
    elif superboard.winner is not None:
        return -100000

    score = 0
    opponent = O if ai_player == X else X
    for b in superboard.grid:
        if b.winner == ai_player:
            score += 500
        elif b.winner == opponent:
            score -= 500
        else:
            score += b.grid.count(ai_player)
            score -= b.grid.count(opponent)

    return score

def minimax(superboard, maximizing=True, ai_player=X, depth=4, alpha=-math.inf, beta=math.inf):
    """
    Minimax with alpha-beta pruning.
    Default depth=4 for performance (was 20).
    """
    superboard.check_winner()
    if superboard.winner == ai_player:
        return (100000, None)
    elif superboard.winner is not None:
        return (-100000, None)

    moves = list(legal_moves(superboard))
    if depth == 0 or not moves:
        return (heuristic(superboard, ai_player), None)

    if maximizing:
        max_eval = -10**9
        best_move = None
        for mv in moves:
            b_idx, pos = mv
            sb_copy = superboard.clone()
            try:
                sb_copy.make_move(pos, board=b_idx)
            except ValueError:
                continue

            eval_score, _ = minimax(sb_copy, False, ai_player, depth-1, alpha, beta)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = mv
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return (max_eval, best_move)
    else:
        min_eval = 10**9
        best_move = None
        for mv in moves:
            b_idx, pos = mv
            sb_copy = superboard.clone()
            try:
                sb_copy.make_move(pos, board=b_idx)
            except ValueError:
                continue

            eval_score, _ = minimax(sb_copy, True, ai_player, depth-1, alpha, beta)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = mv
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return (min_eval, best_move)
