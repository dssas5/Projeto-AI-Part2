import math
import random
from Player import Player


class MCTSNode:
    def __init__(self, board, parent=None, move=None, piece=None):
        self.board = board
        self.parent = parent
        self.move = move
        self.piece = piece

        self.children = []
        self.wins = 0
        self.visits = 0

        self.untried_moves = board.get_valid_moves()

    def ucb1(self):
        if self.visits == 0:
            return float("inf")

        exploitation = self.wins / self.visits
        exploration = math.sqrt(math.log(self.parent.visits) / self.visits)

        return exploitation + 1.41 * exploration

    def best_child(self):
        best = None
        best_value = -1

        for child in self.children:
            value = child.ucb1()

            if value > best_value:
                best_value = value
                best = child

        return best

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        if self.board.is_board_full():
            return True

        if self.board.check_winner(1):
            return True

        if self.board.check_winner(2):
            return True

        return False


class MCTSAIPlayer(Player):
    def __init__(self, piece, max_iterations=1000):
        super().__init__(piece)

        self.max_iterations = max_iterations

        if piece == 1:
            self.opponent_piece = 2
        else:
            self.opponent_piece = 1

    def get_move(self, board):
        root = MCTSNode(board.copy(), piece=self.opponent_piece)

        for i in range(self.max_iterations):
            node = self.select_node(root)
            winner = self.simulate_game(node)
            self.update_values(node, winner)

        if len(root.children) == 0:
            valid_moves = board.get_valid_moves()
            return random.choice(valid_moves)

        best_child = None
        best_visits = -1

        for child in root.children:
            if child.visits > best_visits:
                best_visits = child.visits
                best_child = child

        return best_child.move

    def select_node(self, node):
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return self.expand_node(node)
            else:
                node = node.best_child()

        return node

    def expand_node(self, node):
        move_index = random.randrange(len(node.untried_moves))
        move = node.untried_moves.pop(move_index)

        if node.piece == 1:
            next_piece = 2
        else:
            next_piece = 1

        new_board = node.board.copy()
        new_board.drop_piece(move, next_piece)

        new_node = MCTSNode(
            new_board,
            parent=node,
            move=move,
            piece=next_piece
        )

        node.children.append(new_node)

        return new_node

    def simulate_game(self, node):
        board_copy = node.board.copy()

        if node.piece == 1:
            current_piece = 2
        else:
            current_piece = 1

        while True:
            if board_copy.check_winner(1):
                return 1

            if board_copy.check_winner(2):
                return 2

            if board_copy.is_board_full():
                return 0

            valid_moves = board_copy.get_valid_moves()
            move = random.choice(valid_moves)

            board_copy.drop_piece(move, current_piece)

            if current_piece == 1:
                current_piece = 2
            else:
                current_piece = 1

    def update_values(self, node, winner):
        while node is not None:
            node.visits += 1

            if winner == 0:
                node.wins += 0.5
            elif winner == node.piece:
                node.wins += 1

            node = node.parent