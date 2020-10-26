# ricochet_robots.py: Template para implementação do 1º projeto de Inteligência Artificial 2020/2021.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 12:
# 93717 Guilherme Saraiva
# 93756 Sara Ferreira

from search import Problem, Node, recursive_best_first_search
import sys
import copy


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


def parse_instance(filename: str) -> Board:
    """ Lê o ficheiro cujo caminho é passado como argumento e retorna
    uma instância da classe Board. """

    f = open(filename, "r")
    dim = int(f.readline())
    file_buf = []
    barriers = {}  # pos: [sides]
    robot_pos = {}  # color: pos

    for i in range(4):
        file_buf.append(f.readline())
        robot_pos[file_buf[i][0]] = [int(file_buf[i][2]), int(file_buf[i][4])]
    file_buf.clear()

    buf = f.readline()
    target_color = buf[0]
    target_pos = (int(buf[2]), int(buf[4]))

    barriers_number = int(f.readline())
    for i in range(barriers_number):
        file_buf.append(f.readline())
        if (int(file_buf[i][0]), int(file_buf[i][2])) in barriers:
            barriers[(int(file_buf[i][0]), int(file_buf[i][2]))].append(file_buf[i][4])
        else:
            barriers[(int(file_buf[i][0]), int(file_buf[i][2]))] = [file_buf[i][4]]

    return Board(robot_pos, target_pos, target_color, barriers, dim, barriers_number)


def actions_aux(color: str, state: RRState):
    possible_individual_actions = []

    pos = state.board.robot_pos[color]
    line = pos[0]
    col = pos[1]
    barriers = state.board.barriers_pos
    dim = state.board.dimension

    def is_wall(mov):
        if (line, col) in barriers and mov in barriers[(line, col)]:
            return True
        else:
            if mov == 'u':
                return (line - 1, col) in barriers and 'd' in barriers[(line - 1, col)]
            elif mov == 'd':
                return (line + 1, col) in barriers and 'u' in barriers[(line + 1, col)]
            elif mov == 'r':
                return (line, col + 1) in barriers and 'l' in barriers[(line, col + 1)]
            elif mov == 'l':
                return (line, col - 1) in barriers and 'r' in barriers[(line, col - 1)]

    def has_robot(mov):
        colors = ['Y', 'G', 'R', 'B']
        colors.remove(color)

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


def print_soltuion(solution_n):
    solution_actions = []

    while solution_n.action:
        solution_actions.insert(0, solution_n.action)
        solution_n = solution_n.parent

    print(len(solution_actions))
    for action in solution_actions:
        print(action[0] + ' ' + action[1])


class RicochetRobots(Problem):
    def __init__(self, board: Board):
        """ O construtor especifica o estado inicial. """

        self.initial = RRState(board)
        self.goal = board.target_pos
        super().__init__(initial=self.initial, goal=self.goal)

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

        new_state = copy.deepcopy(state)  # copy actual state to a new state to be modified

        # while action in self.actions(new_state):  # --> Este e' mais lento que o action_aux
        while action in actions_aux(color, new_state):
            if mov == 'u':
                new_state.board.robot_pos[color][0] -= 1
            elif mov == 'd':
                new_state.board.robot_pos[color][0] += 1
            elif mov == 'r':
                new_state.board.robot_pos[color][1] += 1
            elif mov == 'l':
                new_state.board.robot_pos[color][1] -= 1

        return new_state

    def goal_test(self, state: RRState):
        """ Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se o alvo e o robô da
        mesma cor ocupam a mesma célula no tabuleiro. """

        target_color = state.board.target_color
        robot_pos = state.board.robot_position(target_color)

        return robot_pos == self.goal

    def h(self, node: Node):
        """ Função heuristica utilizada para a procura A*. """

        if node.action:
            x1, y1 = node.state.board.robot_position(node.action[0])
        else:
            target_color = node.state.board.target_color
            x1, y1 = node.state.board.robot_position(target_color)

        x2, y2 = self.goal

        return abs(x2 - x1) + abs(y2 - y1)  # Manhattan Heuristic Function


if __name__ == "__main__":
    # Ler o ficheiro de input de sys.argv[1],
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.

    # Ler tabuleiro do stdin
    board = parse_instance(sys.argv[1])

    # Criar uma instância de RicochetRobots
    problem = RicochetRobots(board)

    # Obter o nó solução usando a procura recursive_best_first_search:
    solution_node = recursive_best_first_search(problem)

    # Escrever a solucao
    print_soltuion(solution_node)














