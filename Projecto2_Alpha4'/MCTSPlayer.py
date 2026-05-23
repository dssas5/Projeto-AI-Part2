import math
import random
from Player import Player


class MCTSNode:
    def __init__(self, board, parent=None, move=None, piece=None):
        self.board = board
        self.parent = parent
        self.move = move          # coluna jogada para chegar aqui
        self.piece = piece        # peça que jogou para chegar aqui
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = board.get_valid_moves()

    def ucb1(self, c=1.41):
        if self.visits == 0:
            return math.inf       # nós não visitados têm prioridade máxima
        return (self.wins / self.visits) + c * math.sqrt(math.log(self.parent.visits) / self.visits)

    def best_child(self):
        return max(self.children, key=lambda n: n.ucb1())

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def is_terminal(self):
        return (self.board.is_board_full() or
                self.board.check_winner(1) or
                self.board.check_winner(2))


class MCTSAIPlayer(Player):
    def __init__(self, piece, max_iterations=1000):
        super().__init__(piece)
        self.max_iterations = max_iterations
        self.opponent_piece = 2 if piece == 1 else 1

    def get_move(self, board):
        root = MCTSNode(board.copy(), piece=self.opponent_piece)

        for _ in range(self.max_iterations):
            node = self._select(root)       # 1. Seleção
            result = self._simulate(node)   # 2+3. Expansão + Simulação
            self._backpropagate(node, result)  # 4. Retropropagação

        if not root.children:
            return random.choice(board.get_valid_moves())

        # escolher o filho mais visitado (mais robusto que o de maior win rate)
        best = max(root.children, key=lambda n: n.visits)
        return best.move

    def _select(self, node):
        while not node.is_terminal():
            if not node.is_fully_expanded():
                return self._expand(node)   # expandir se ainda há moves por tentar
            node = node.best_child()        # descer pelo UCB1
        return node

    def _expand(self, node):
        move = node.untried_moves.pop(random.randrange(len(node.untried_moves)))
        next_piece = 2 if node.piece == 1 else 1
        new_board = node.board.copy()
        new_board.drop_piece(move, next_piece)
        child = MCTSNode(new_board, parent=node, move=move, piece=next_piece)
        node.children.append(child)
        return child

    def _simulate(self, node):
        sim_board = node.board.copy()
        current_piece = 2 if node.piece == 1 else 1

        while True:
            if sim_board.check_winner(1): return 1
            if sim_board.check_winner(2): return 2
            if sim_board.is_board_full():  return 0

            col = random.choice(sim_board.get_valid_moves())
            sim_board.drop_piece(col, current_piece)
            current_piece = 2 if current_piece == 1 else 1

    def _backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            if result == 0:
                node.wins += 0.5        # empate = valor neutro
            elif result == node.piece:
                node.wins += 1          # vitória = crédito total
            node = node.parent