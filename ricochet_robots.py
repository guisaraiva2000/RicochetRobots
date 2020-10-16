# ricochet_robots.py: Template para implementação do 1º projeto de Inteligência Artificial 2020/2021.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

from search import Problem, Node, astar_search, breadth_first_tree_search, \
    depth_first_tree_search, greedy_search
import sys


class RRState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = RRState.state_id
        RRState.state_id += 1

    def __lt__(self, other):
        """ Este método é utilizado em caso de empate na gestão da lista
        de abertos nas procuras informadas. """
        return self.id < other.id


class Board:
    """ Representacao interna de um tabuleiro de Ricochet Robots. """

    def __init__(self, robot_pos, target_pos, target_color, barriers_pos, dimension, barriers_num):
        self.robot_pos = robot_pos
        self.target_pos = target_pos
        self.target_color = target_color
        self.barriers_pos = barriers_pos
        self.dimension = dimension
        self.barriers_num = barriers_num

    def robot_position(self, robot: str):
        """ Devolve a posição atual do robô passado como argumento. """
        return tuple(self.robot_pos[robot])

    def set_robot_position(self, robot: str, new_pos):
        """ Muda a posição do robô passado como argumento. """
        self.robot_pos[robot] = new_pos


def parse_instance(filename: str) -> Board:
    """ Lê o ficheiro cujo caminho é passado como argumento e retorna
    uma instância da classe Board. """

    f = open(filename, "r")
    dim = int(f.readline())
    file_buf = []
    barriers = {}
    robot_pos = {}

    for i in range(dim):
        file_buf.append(f.readline())
        robot_pos[file_buf[i][0]] = [int(file_buf[i][2]), int(file_buf[i][4])]
    file_buf.clear()

    buf = f.readline()
    target_color = buf[0]
    target_pos = (int(buf[2]), int(buf[4]))

    barriers_number = int(f.readline())
    for i in range(barriers_number):
        file_buf.append(f.readline())
        barriers[(int(file_buf[i][0]), int(file_buf[i][2]))] = file_buf[i][4]

    return Board(robot_pos, target_pos, target_color, barriers, dim, barriers_number)


def actions_aux(color: str, state: RRState):
    possible_individual_actions = []

    pos = state.board.robot_pos[color]
    line = pos[0]
    col = pos[1]
    barriers = state.board.barriers_pos
    dim = state.board.dimension

    def is_wall(mov):
        if (line, col) in barriers and barriers[(line, col)] == mov:
            return True
        else:
            if mov == 'u':
                return (line - 1, col) in barriers and barriers[(line - 1, col)] == 'd'
            elif mov == 'd':
                return (line + 1, col) in barriers and barriers[(line + 1, col)] == 'u'
            elif mov == 'r':
                return (line, col + 1) in barriers and barriers[(line, col + 1)] == 'l'
            elif mov == 'l':
                return (line, col - 1) in barriers and barriers[(line, col - 1)] == 'r'

    def has_robot(mov):
        colors = ['G', 'R', 'B', 'Y']

        if mov == 'u':
            for c in colors:
                if (line - 1, col) == state.board.robot_position(c):
                    return True
        elif mov == 'd':
            for c in colors:
                if (line + 1, col) == state.board.robot_position(c):
                    return True
        elif mov == 'r':
            for c in colors:
                if (line, col + 1) == state.board.robot_position(c):
                    return True
        elif mov == 'l':
            for c in colors:
                if (line, col - 1) == state.board.robot_position(c):
                    return True

    if line != 1 and not is_wall('u') and not has_robot('u'):
        possible_individual_actions.append((color, 'u'))
    if line != dim and not is_wall('d') and not has_robot('d'):
        possible_individual_actions.append((color, 'd'))
    if col != dim and not is_wall('r') and not has_robot('r'):
        possible_individual_actions.append((color, 'r'))
    if col != 1 and not is_wall('l') and not has_robot('l'):
        possible_individual_actions.append((color, 'l'))

    return possible_individual_actions


class RicochetRobots(Problem):
    def __init__(self, board: Board):
        """ O construtor especifica o estado inicial. """

        self.initial = RRState(board)
        self.goal = board.target_pos
        super().__init__(self.initial, self.goal)
        self.mov_buf = []


    def actions(self, state: RRState):
        """ Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento. """

        colors = ['G', 'R', 'B', 'Y']
        possible_actions = []

        for color in colors:
            possible_actions.extend(actions_aux(color, state))

        return possible_actions

    def result(self, state: RRState, action):
        """ Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação retornada deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state). """

        color = action[0]
        mov = action[1]

        while action in self.actions(state):
            if mov == 'u':
                state.board.robot_pos[color][0] -= 1
            elif mov == 'd':
                state.board.robot_pos[color][0] += 1
            elif mov == 'r':
                state.board.robot_pos[color][1] += 1
            elif mov == 'l':
                state.board.robot_pos[color][1] -= 1

        return state

    def goal_test(self, state: RRState):
        """ Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se o alvo e o robô da
        mesma cor ocupam a mesma célula no tabuleiro. """

        target = state.board.target_pos
        target_color = state.board.target_color
        robot_pos = state.board.robot_position(target_color)

        return robot_pos == target

    def h(self, node: Node):
        """ Função heuristica utilizada para a procura A*. """
        target_color = node.state.board.target_color

        # Manhattan Heuristic Function
        x1, y1 = node.state.board.robot_position(target_color)
        x2, y2 = self.goal

        return abs(x2 - x1) + abs(y2 - y1)


if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro de input de sys.argv[1],
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.

    # Ler tabuleiro do ficheiro "i1.txt":
    board = parse_instance("i1.txt")

    # Criar uma instância de RicochetRobots:
    problem = RicochetRobots(board)

    # Obter o nó solução usando a procura A*:
    solution_node = breadth_first_tree_search(problem)







