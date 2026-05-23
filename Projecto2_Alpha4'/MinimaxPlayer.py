import math
from Player import Player


class MinimaxAIPlayer(Player):
    def __init__(self, piece, max_depth=5):
        super().__init__(piece)
        self.max_depth = max_depth
        self.opponent_piece = 2 if piece == 1 else 1

    def get_move(self, board):
        valid_moves = board.get_valid_moves()
        best_score = -math.inf
        best_col = valid_moves[len(valid_moves) // 2]  # default: centro

        for col in valid_moves:
            new_board = board.copy()
            new_board.drop_piece(col, self.piece)
            score = self._minimax(new_board, self.max_depth - 1, -math.inf, math.inf, False)
            if score > best_score:
                best_score = score
                best_col = col

        return best_col

    def _minimax(self, board, depth, alpha, beta, maximizing):
        # Verificar estados terminais
        if board.check_winner(self.piece):
            return 100000 + depth        # vitória mais rápida vale mais
        if board.check_winner(self.opponent_piece):
            return -(100000 + depth)     # derrota mais rápida vale menos
        if board.is_board_full() or depth == 0:
            return self.evaluate_board(board, self.piece)

        valid_moves = board.get_valid_moves()

        if maximizing:
            value = -math.inf
            for col in valid_moves:
                new_board = board.copy()
                new_board.drop_piece(col, self.piece)
                value = max(value, self._minimax(new_board, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break              # poda alpha-beta
            return value
        else:
            value = math.inf
            for col in valid_moves:
                new_board = board.copy()
                new_board.drop_piece(col, self.opponent_piece)
                value = min(value, self._minimax(new_board, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if alpha >= beta:
                    break              # poda alpha-beta
            return value

    def evaluate_board(self, board, player):
        opponent = 2 if player == 1 else 1
        score = 0
        n = board.n_connect
        grid = board.grid
        rows = board.rows
        cols = board.cols

        # Preferência pela coluna central
        center_col = cols // 2
        center_array = [grid[r][center_col] for r in range(rows)]
        score += center_array.count(player) * 3

        def score_window(window):
            s = 0
            p_count = window.count(player)
            o_count = window.count(opponent)
            empty   = window.count(0)
            if p_count == n:                        # vitória
                s += 10000
            elif p_count == n - 1 and empty == 1:  # quase vitória
                s += 50
            elif p_count == n - 2 and empty == 2:  # sequência de 2
                s += 10
            if o_count == n - 1 and empty == 1:    # bloquear adversário
                s -= 80
            return s

        # Horizontal
        for r in range(rows):
            for c in range(cols - n + 1):
                window = [grid[r][c + i] for i in range(n)]
                score += score_window(window)

        # Vertical
        for c in range(cols):
            for r in range(rows - n + 1):
                window = [grid[r + i][c] for i in range(n)]
                score += score_window(window)

        # Diagonal /
        for r in range(n - 1, rows):
            for c in range(cols - n + 1):
                window = [grid[r - i][c + i] for i in range(n)]
                score += score_window(window)

        # Diagonal \
        for r in range(rows - n + 1):
            for c in range(cols - n + 1):
                window = [grid[r + i][c + i] for i in range(n)]
                score += score_window(window)

        return score