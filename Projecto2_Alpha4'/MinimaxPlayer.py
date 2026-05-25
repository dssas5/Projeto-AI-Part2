import math
from Player import Player


class MinimaxAIPlayer(Player):
    def __init__(self, piece, max_depth=5):
        super().__init__(piece)

        self.max_depth = max_depth

        if piece == 1:
            self.opponent_piece = 2
        else:
            self.opponent_piece = 1

    def get_move(self, board):
        valid_moves = board.get_valid_moves()

        best_score = -math.inf
        best_col = valid_moves[0]

        # tentar começar pelo centro, se existir
        middle = board.cols // 2
        if middle in valid_moves:
            best_col = middle

        for col in valid_moves:
            new_board = board.copy()
            new_board.drop_piece(col, self.piece)

            score = self.minimax(
                new_board,
                self.max_depth - 1,
                -math.inf,
                math.inf,
                False
            )

            if score > best_score:
                best_score = score
                best_col = col

        return best_col

    def minimax(self, board, depth, alpha, beta, maximizing):
        if board.check_winner(self.piece):
            return 100000 + depth

        if board.check_winner(self.opponent_piece):
            return -100000 - depth

        if board.is_board_full() or depth == 0:
            return self.evaluate_board(board, self.piece)

        valid_moves = board.get_valid_moves()

        if maximizing:
            best_value = -math.inf

            for col in valid_moves:
                new_board = board.copy()
                new_board.drop_piece(col, self.piece)

                value = self.minimax(
                    new_board,
                    depth - 1,
                    alpha,
                    beta,
                    False
                )

                if value > best_value:
                    best_value = value

                if best_value > alpha:
                    alpha = best_value

                if alpha >= beta:
                    break

            return best_value

        else:
            best_value = math.inf

            for col in valid_moves:
                new_board = board.copy()
                new_board.drop_piece(col, self.opponent_piece)

                value = self.minimax(
                    new_board,
                    depth - 1,
                    alpha,
                    beta,
                    True
                )

                if value < best_value:
                    best_value = value

                if best_value < beta:
                    beta = best_value

                if alpha >= beta:
                    break

            return best_value

    def evaluate_board(self, board, player):
        if player == 1:
            opponent = 2
        else:
            opponent = 1

        score = 0

        n = board.n_connect
        grid = board.grid
        rows = board.rows
        cols = board.cols

        center_col = cols // 2

        for r in range(rows):
            if grid[r][center_col] == player:
                score += 3

        # verificar horizontais
        for r in range(rows):
            for c in range(cols - n + 1):
                window = []

                for i in range(n):
                    window.append(grid[r][c + i])

                score += self.evaluate_window(window, player, opponent, n)

        # verificar verticais
        for c in range(cols):
            for r in range(rows - n + 1):
                window = []

                for i in range(n):
                    window.append(grid[r + i][c])

                score += self.evaluate_window(window, player, opponent, n)

        # verificar diagonais /
        for r in range(n - 1, rows):
            for c in range(cols - n + 1):
                window = []

                for i in range(n):
                    window.append(grid[r - i][c + i])

                score += self.evaluate_window(window, player, opponent, n)

        # verificar diagonais \
        for r in range(rows - n + 1):
            for c in range(cols - n + 1):
                window = []

                for i in range(n):
                    window.append(grid[r + i][c + i])

                score += self.evaluate_window(window, player, opponent, n)

        return score

    def evaluate_window(self, window, player, opponent, n):
        score = 0

        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(0)

        if player_count == n:
            score += 10000

        elif player_count == n - 1 and empty_count == 1:
            score += 50

        elif player_count == n - 2 and empty_count == 2:
            score += 10

        if opponent_count == n - 1 and empty_count == 1:
            score -= 80

        return score