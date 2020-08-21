import time
import math
import copy


class Halma():
    def __init__(self, config):
        self.board_size = 16
        self.black_camp = []
        self.white_camp = []
        self.non_goals = []
        self.board = config['board-configuration']
        self.color = config['current-color'][0]
        self.opponent_color = 'B' if self.color == 'W' else 'W'
        self.time_limit = config['time-limit']
        self.pawn_locations = []
        self.opponent_pawn_locations = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if row + col <= 5 and row < 5 and col < 5:
                    self.black_camp.append((row, col))
                elif row + col >= 25 and row > 10 and col > 10:
                    self.white_camp.append((row, col))
                else:
                    self.non_goals.append((row, col))
        self.white_goals = self.black_camp
        self.black_goals = self.white_camp
        if self.color == 'B':
            self.goals = self.black_goals
            self.my_camp = self.white_goals
            self.opponent_color = 'W'
        else:
            self.goals = self.white_goals
            self.my_camp = self.black_goals
            self.opponent_color = 'B'
        self.get_pawn_locations()
        self.use_alternate_heuristic = False
        if config['move-configuration'] == 'SINGLE':
            val, output_move = self.minimax(2, self.color)
            self.write_output(output_move)
        else:
            depth = 3
            count = 0
            for every_pawn in self.pawn_locations:
                if every_pawn in self.my_camp:
                    count += 1

            if count > 13:
                depth = 2

            if float(self.time_limit) < 120:
                depth = 2
            if float(self.time_limit) < 10:
                depth = 1

            pawn_count = 0
            opposite_pawn_count = 0
            for every_pawn in self.pawn_locations:
                if every_pawn in self.goals:
                    pawn_count += 1
            for every_opposite_pawn in self.opponent_pawn_locations:
                if every_opposite_pawn in self.my_camp:
                    opposite_pawn_count += 1
            if pawn_count > 5 or opposite_pawn_count > 5:
                self.use_alternate_heuristic = True

            val, move = self.minimax(depth, self.color)
            self.write_output(move)

    def write_output(self, move_list):
        file_out = open("output.txt", "w")
        newline = ''
        for move in move_list:
            file_out.write(newline + move)
            newline = '\n'

    def display_board(self):
        for i in range(self.board_size):
            print(self.board[i])

    def get_pawn_locations(self):
        for col in range(self.board_size):
            for row in range(self.board_size):
                if self.board[row][col] == self.color:
                    self.pawn_locations.append((row, col))
                elif self.board[row][col] == self.opponent_color:
                    self.opponent_pawn_locations.append((row, col))

    def get_next_moves(self, player):
        moves = []  # All possible moves
        flag = False
        for col in range(self.board_size):
            for row in range(self.board_size):
                current_pawn = self.board[row][col]
                if current_pawn != player:
                    continue
                if (row, col) in (self.black_camp if player == 'B' else self.white_camp):
                    to = []
                    moves_list = self.get_moves_for_pawn(row, col, player, to)
                    invalid_moves = []
                    for move in moves_list:
                        if abs(move[0] - row) > 1 or abs(move[1] - col) > 1:
                            if player == 'B':
                                if move[0] < row or move[1] < col:
                                    invalid_moves.append(move)
                            else:
                                if move[0] > row or move[1] > col:
                                    invalid_moves.append(move)

                    for every_invalid_move in invalid_moves:
                        moves_list.remove(every_invalid_move)

                    move = {
                        'from': (col, row),
                        'to': to,
                        'movesList': moves_list,
                    }
                    moves.append(move)

        for every_move in moves:
            if every_move['movesList']:
                flag = True
                break

        if flag:
            to_be_checked_moves = copy.deepcopy(moves)
            for every_pawn_move in to_be_checked_moves:
                invalid_moves = []
                for every_move in every_pawn_move['movesList']:
                    if every_move in (self.black_camp if player == 'B' else self.white_camp):
                        invalid_moves.append(every_move)
                for each in invalid_moves:
                    every_pawn_move['movesList'].remove(each)

            for every_pawn_move in to_be_checked_moves:
                if every_pawn_move['movesList']:
                    return to_be_checked_moves

            return moves
        else:
            moves = []
            for col in range(self.board_size):
                for row in range(self.board_size):
                    current_pawn = self.board[row][col]
                    if current_pawn != player:
                        continue
                    to = []
                    moves_list = self.get_moves_for_pawn(row, col, player, to)

                    invalid_moves = []
                    for move in moves_list:
                        if abs(move[0] - row) > 1 or abs(move[1] - col) > 1:
                            if player == 'B':
                                if move not in self.black_goals:
                                    if move[0] < row or move[1] < col:
                                        invalid_moves.append(move)
                            else:
                                if move not in self.white_goals:
                                    if move[0] > row or move[1] > col:
                                        invalid_moves.append(move)
                            if ((row, col) in (self.black_goals if player == 'B' else self.white_goals)) and (
                                    move in self.non_goals):
                                if move not in invalid_moves:
                                    invalid_moves.append(move)
                        else:
                            if ((row, col) in (self.black_goals if player == 'B' else self.white_goals)) and (
                                    move in self.non_goals):
                                invalid_moves.append(move)

                    for every_invalid_move in invalid_moves:
                        moves_list.remove(every_invalid_move)

                    move = {
                        'from': (col, row),
                        'to': to,
                        'movesList': moves_list,
                    }
                    moves.append(move)

            check_moves = copy.deepcopy(moves)
            invalid_moves = []
            for each in check_moves:
                if (each['from'][1], each['from'][0]) in (self.black_goals if player == 'B' else self.white_goals):
                    invalid_moves.append(each)
            for i in invalid_moves:
                check_moves.remove(i)
            for each in check_moves:
                if each['movesList']:
                    return check_moves
            return moves

    def get_moves_for_pawn(self, row, col, player, to, moves=None, adj=True, jump_move_per_pawn=None):
        if moves is None:
            moves = []

        # List of valid squares to move to
        valid_squares = self.black_goals + self.white_goals + self.non_goals
        if (row, col) not in (self.black_camp if player == 'B' else self.white_camp):
            my_own_camp = self.black_camp if player == 'B' else self.white_camp
            for each_camp_pos in my_own_camp:
                valid_squares.remove(each_camp_pos)
        if (row, col) in (self.white_goals if player == 'W' else self.black_goals):
            for non_goal in self.non_goals:
                valid_squares.remove(non_goal)

        for col_vector in range(-1, 2):
            for row_vector in range(-1, 2):

                changed_row = row + row_vector
                changed_col = col + col_vector

                if adj:
                    move_per_pawn = []

                if ((changed_row == row and changed_col == col) or
                        changed_row < 0 or changed_col < 0 or changed_row >= self.board_size or changed_col >= self.board_size):
                    continue

                if (changed_row, changed_col) not in valid_squares:
                    continue

                if self.board[changed_row][changed_col] == '.':
                    if adj:
                        if player == 'B':
                            if changed_row < row or changed_col < col:
                                continue
                        else:
                            if changed_row > row or changed_col > col:
                                continue

                        moves.append((changed_row, changed_col))
                        move_string = 'E ' + str(col) + ',' + str(row) + ' ' + str(changed_col) + ',' + str(changed_row)
                        move_per_pawn.append(move_string)
                        to.append(move_per_pawn)
                    continue

                if jump_move_per_pawn is None:
                    jump_move_per_pawn = []
                else:
                    if jump_move_per_pawn:
                        key = jump_move_per_pawn[-1].split(' ')[2]
                        while key != str(col) + ',' + str(row):
                            jump_move_per_pawn = jump_move_per_pawn[:]
                            jump_move_per_pawn.pop()
                            if jump_move_per_pawn and jump_move_per_pawn not in to:
                                placeholder = jump_move_per_pawn[:]
                                to.append(placeholder)
                            if not jump_move_per_pawn:
                                break
                            key = jump_move_per_pawn[-1].split(' ')[2]

                changed_row = changed_row + row_vector
                changed_col = changed_col + col_vector

                if (changed_row < 0 or changed_col < 0 or
                        changed_row >= self.board_size or changed_col >= self.board_size):
                    continue

                if (changed_row, changed_col) in moves or (changed_row, changed_col) not in valid_squares:
                    continue

                if self.board[changed_row][changed_col] == '.':
                    moves.insert(0, (changed_row, changed_col))  # Prioritize jumps
                    move_string = 'J ' + str(col) + ',' + str(row) + ' ' + str(changed_col) + ',' + str(changed_row)
                    jump_move_per_pawn.append(move_string)
                    self.get_moves_for_pawn(changed_row, changed_col, player, to, moves, False, jump_move_per_pawn)
                    if jump_move_per_pawn not in to:
                        to.append(jump_move_per_pawn)

        return moves

    def utility_distance(self, player):
        opponent_player = 'B' if player == 'W' else 'W'

        def point_distance(p0, p1):
            return math.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)

        value = 0

        if self.use_alternate_heuristic:
            goals = self.black_goals if player == 'B' else self.white_goals
            other_goals = self.white_goals if player == 'B' else self.black_goals

            for col in range(self.board_size):
                for row in range(self.board_size):
                    if self.board[row][col] == player:
                        dist = [point_distance((row, col), g) for g in goals if self.board[g[0]][g[1]] != player]
                        value += max(dist) if len(dist) else -50
                    elif self.board[row][col] == opponent_player:
                        dist = [point_distance((row, col), g) for g in other_goals if
                                self.board[g[0]][g[1]] != opponent_player]
                        value -= max(dist) if len(dist) else -50
        else:
            goal = (0, 0) if player == 'W' else (15, 15)
            opponent_goal = (0, 0) if player == 'B' else (15, 15)
            for col in range(self.board_size):
                for row in range(self.board_size):
                    if self.board[row][col] == player:
                        dist = point_distance((row, col), goal)
                        value += dist if dist > 0 else -50
                    elif self.board[row][col] == opponent_player:
                        dist = point_distance((row, col), opponent_goal)
                        value -= dist if dist > 0 else -50

        if player == self.color:
            value *= -1
        return value

    def minimax(self, depth, max_player, a=float("-inf"), b=float("inf"), max_element=True):
        has_won = self.if_won()

        if (depth == 0) or has_won:
            return self.utility_distance(max_player), None

        best_move = None
        if max_element:
            best_value = float("-inf")
            moves = self.get_next_moves(max_player)
        else:
            best_value = float("inf")
            moves = self.get_next_moves(('B' if max_player == 'W' else 'B'))

        for move in moves:
            for to in move["movesList"]:
                self.board[to[0]][to[1]] = self.board[move['from'][1]][move['from'][0]]
                self.board[move['from'][1]][move['from'][0]] = '.'
                val, xyz = self.minimax(depth - 1, max_player, a, b, not max_element)
                self.board[move['from'][1]][move['from'][0]] = self.board[to[0]][to[1]]
                self.board[to[0]][to[1]] = '.'
                if max_element and (val > best_value):
                    best_value = val
                    move_flag = False
                    for mov in move['to']:
                        i = len(mov) - 1
                        while i >= 0:
                            col, row = mov[i].split(' ')[2].split(',')
                            if (int(row), int(col)) == to:
                                if i == len(mov) - 1:
                                    best_move = mov
                                else:
                                    best_move = mov[0:i + 1]
                                move_flag = True
                                break
                            i -= 1
                        if move_flag:
                            break
                    a = max(a, val)
                if (not max_element) and (val < best_value):
                    best_value = val
                    move_flag = False
                    for mov in move['to']:
                        i = len(mov) - 1
                        while i >= 0:
                            col, row = mov[i].split(' ')[2].split(',')
                            if (int(row), int(col)) == to:
                                if i == len(mov) - 1:
                                    best_move = mov
                                else:
                                    best_move = mov[0:i + 1]
                                move_flag = True
                                break
                            i -= 1
                        if move_flag:
                            break
                    b = min(b, val)
                if b <= a:
                    return best_value, best_move
        return best_value, best_move

    def if_won(self):
        flag = False
        for every_black_goal in self.black_goals:
            if self.board[every_black_goal[0]][every_black_goal[1]] != 'B':
                flag = True
                break
        if not flag:
            return True
        flag = False
        for every_white_goal in self.white_goals:
            if self.board[every_white_goal[0]][every_white_goal[1]] != 'W':
                flag = True
                break
        if not flag:
            return True
        return False


if __name__ == "__main__":
    halma = Halma()
