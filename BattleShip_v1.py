from random import randint



class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Color:
    yellow2 = '\033[1;35m'
    reset = '\033[0m'
    blue = '\033[0;34m'
    yellow = '\033[1;93m'
    red = '\033[1;93m'
    counter1 = '\033[0;37m'

    @staticmethod
    def set_color(text, color):
        return color + text + Color.reset


class Cell():
    empty_cell = Color.set_color('O', Color.yellow2)  # пустой корабль
    ship_cell = Color.set_color('■', Color.blue)  # корабль
    damaged_ship = Color.set_color('X', Color.red)  # уничтожен
    counter_cell = Color.set_color('•', Color.counter1)  # промах
    miss_cell = Color.set_color('•', Color.yellow)  # контур


class Ship:
    def __init__(self, bow, l, rotation):
        self.bow = bow
        self.l = l
        self.rotation = rotation
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.rotation == 0:
                cur_x += i

            elif self.rotation == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=10):
        self.size = size
        self.hid = hid

        self.count = 0
        self.cells = [[Cell.empty_cell] * size for i in range(size)]
        
        self.busy = []
        self.ships = []

    def show_field(self):
        res = "  "
        res += '  '
        for i in range(10):
            res = {chr(ord('A') + A): A+1 for A in range(10)}
            # res += chr(ord('A') + i) + " " + " "
        res = "\n"
        for i in range(10):
            res += f" {i} ".format(i)
            for j in range(10):
                if self.cells[i][j]:
                    cell = self.cells[i][j]
                else:
                    cell = Cell.miss_cell if (i, j) in self.size else Cell.damaged_ship
                res += " {} ".format(cell)
            res += "  \n"

            if self.hid:
                res = res.replace(Cell.ship_cell, Cell.empty_cell)

        return res

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.cells[d.x][d.y] = Cell.ship_cell
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.cells[cur.x][cur.y] = Cell.counter_cell
                    self.busy.append(cur)

    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.cells[d.x][d.y] = Cell.damaged_ship
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.cells[d.x][d.y] = Cell.miss_cell
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 9), randint(0, 9))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:

    def __init__(self, size=10):
        self.size = size

        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        board = Board()
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):

        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board.show_field())
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board.show_field())
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 10:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 10:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
