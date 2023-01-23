from random import randint

class FieldException(Exception): #Пропускаем исключения для будущего поля
    pass

class FieldOutExeption(FieldException): #Класс, который ссылается на Класс "Пропуск исключений" и возвращает предупреждение
    def __str__(self):
        return "Выберите поле внутри доски, а не за ней"

class FieldCloseException(FieldException): #Стреляем на поле, которое уже попадали
    def __str__(self):
        return 'Выберите другую клетку, сюда уже попадали'

class FieldBadShipException(FieldException): #Пропускаем, если не попадаем в корабль, а летит в молоко
    pass

class Point:

    def __init__(self, x, y): #Координаты точек
        self.x = x
        self.y = y

    def __eq__(self, enother): #Cравнение точек между собой
        return self.x == enother.x and self.y == enother.y

    def __repr__(self): #Функция, возвращающая координаты точки. Потом это удобно для внесения в список.
        return f"Point{self.x}, {self.y}"


class Ship:
    def __init__(self, coord , length, orient):
        self.coord = coord #Координаты, которые будут передаваться из Point
        self.length = length #Длина корабля
        self.orient = orient #Ориентация корабля 0 - вертикально, 1 - горизонтально
        self.lives = length #Количество жизней = длине корабля

    @property
    def points(self):
        ship_points = [] #Список точек, которые буду остроить корабль
        for i in range(self.length): #Идем по длине корабля
            new_x = self.coord.x #отдельно присваиваем из класса Points координаты x y
            new_y = self.coord.y

            if self.orient == 0: #Если ориентация вертикальная, то добавляем по одному к х
                new_x += i

            elif self.orient == 1: #Если ориантеция горизонтальная, то добавляем по одному к y
                new_y += i

            ship_points.append(Point(new_x, new_y)) #Добавляем наши точки в список

        return ship_points #Возвращаем список кораблей

    def shoot(self, shot): #Функция выстрела (проверка - попал или нет)
        return shot in self.points


class Field:
    def __init__(self, hide=False, size=6):
        self.size = size #Размер поля - 6х6
        self.hide = hide    #Переменная, отвечающая за сокрытие поля, пока не скрываем

        self.count = 0 #Счетчик жизней

        self.field = [["O"] * size for _ in range(size)] #Создание самого поля

        self.busy = [] #Список занятых полей (либо там есть корабль, либо мы туда уже стреляли)
        self.ships = [] #список вообще всех кораблей

    def add_ship(self, ship):

        for p in ship.points: #Чтобы добавить корабль, берем по одному элементу из списка ship.points и сначала проверяем на исключение. Если попадает вне поля или на уже занятую клетку, то получаем ошибку и возвращаем соответствующее выражение
            if self.out_of_field(p) or p in self.busy:
                raise FieldBadShipException()
        for p in ship.points: #Опять идем по всем точкам корабля и на определенны места ставим корабли, добавляем в список занятых точек
            self.field[p.x][p.y] = "■"
            self.busy.append(p)

        self.ships.append(ship) #Добавление в список вообще всех кораблей
        self.contour(ship) #Обводим по контуру, чтоб рядом случайно не поставить другой корабль

    def contour(self, ship, verb=False):
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ] #Поле вокруг корабля
        for sh in ship.points: #Для корабля из списка координат
            for i, j in around: #Пройти по всем элементам списка
                next = Point(sh.x + i, sh.y + j) #Смещаем заданную координату на каждое значение пар из списка
                if not (self.out_of_field(next)) and next not in self.busy: #Проверка для точки, если она не вне поля и не занята, то мы ее добавляем в список занятых точек и помечаем ее точечкой, чтоб туда не вставить что-то еще левое
                    if verb:
                        self.field[next.x][next.y] = "."
                    self.busy.append(next)

    def __str__(self): #Вывод поля
        header = "" #Заголовок поля
        header += "  | 1 | 2 | 3 | 4 | 5 | 6 |" #Добавляем в заголовок номера столбов и строк
        for i, j in enumerate(self.field): #Строим поле: идем по столбцам и строкам в поле self.field и выводим поле через палочки
            header += f"\n{i + 1} | " + " | ".join(j) + " |"

        if self.hide: #Если переменная self.hide = правда, то заменить поля с кораблями на пустое, это для сокрытия поля противника
            header = header.replace("■", "O")
        return header

    def out_of_field(self, cord): #Проверка на наличие точки вне доски
        return not ((0 <= cord.x < self.size) and (0 <= cord.y < self.size))

    def shot(self, p): #Метод выстрела
        if self.out_of_field(p): #Выбрасываем ошибку, если вне поля
            raise FieldOutExeption()

        if p in self.busy: #Выбрасываем ошибку, если точка по уже занятой
            raise FieldCloseException()

        self.busy.append(p) #Продолжаем добавлять в занятые, чтоб потом в нее не попасть

        for ship in self.ships: #Начало перестрелки
            if ship.shoot(p): #Вызов метода поражения
                ship.lives -= 1 #Если сработало, то уменьшаем количество жизней и длину корабля на 1
                self.field[p.x][p.y] = "X" #Отмечаем пораженную клетку корабля Х
                if ship.lives == 0: #Если счетчик жизней корабля равен 0, то добавляем себе победу
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Вы разбили корабль!")
                    return False
                else:
                    print("Вы полали в корабль!") #Если счетчик жизней корабля не равен 0 и мы попали, то выводим соответствующее выражение
                    return True

        self.field[p.x][p.y] = "." #И если там не было корабля, а были только точки, то выводим сообщение
        print("Вы не попали!")
        return False

    def begin(self):
        self.busy = [] #Обнуление списка занятых кораблей, чтобы его можно было повторно использовать в игре для вывода поля, где игрок будет стрелять, а не создавать отдельный список


class Gamer:
    def __init__(self, field, computer): #Для игрока нам нужно две доски - его и противника (но корабли на ней скрыты, как прописано выше)
        self.field = field
        self.computer = computer

    def ask(self): #метод, который потом понадобится для потомков этого класса. Вылавливает ошибку, если наследный класс не переопределит данный метод
        raise NotImplementedError()

    def shoot_in_place(self): #метод для бесконечного выстрела
        while True:
            try:
                ask_coord = self.ask() #Просим комп или человека дать координаты выстрела
                try_again = self.computer.shot(ask_coord)
                return try_again #Возвращается в случае хорошнго выстрела
            except FieldException as e: #В случае плохого выстрела печатаем исключение и продолжаем цикл далее
                print(e)


class Computer(Gamer): #Ход компьютера
    def ask(self): #Спрашиваем его о координатах выстрела, метод которого ранее был прописан в классе Геймер
        p = Point(randint(0, 5), randint(0, 5))  #Он дает случайное месьто с координатами
        print(f"Ход компьютера: {p.x + 1} {p.y + 1}") #Выводит координаты, прибавив к ним 1 для точного места
        return p #Возвращаем координаты


class Person(Gamer): #Ход человека
    def ask(self): #Спрашиваем человека о коорднатах и запускаем цикл
        while True:
            cords = input("Введите координаты - Х и Y:  ").split() #Разделим наши координаты и создадим список, чтоб потом егшо передать в Point

            if len(cords) != 2: #Проверяем количество координат, если их больше, то выводим просьбу о повторном вводе
                print(f" Координат должно быть 2, a не {len(cords)} ")
                continue

            x, y = cords #Придаем нашим переменным координаты, введеные пользователем

            if not (x.isdigit()) or not (y.isdigit()): #Проверка на принадлежность числу, а не букве
                print(" Это должны быть числа, а не буквы и другие знаки ")
                continue

            x, y = int(x), int(y) #Перезаписываем координаты уже в формате чисел

            return Point(x - 1, y - 1) #Возвращаем координаты в класс Point для дальнейшей работы


class Game:
    def __init__(self, size=6): #Задаем информацию для поля
        self.size = size
        gamer = self.random_field() #Поле игрока
        computer = self.random_field()  #Поле компьютера
        computer.hide = True  #Скрываем поле компьютера

        self.computer = Computer(computer, gamer)  #Передача полей компьютеру и игроку в соответствующие классфы
        self.gamer = Person(gamer, computer)

    def random_field(self):  #Генерация игрового поля
        field = None
        while field is None:  #Покуда возващаем None, генерируем поле зано
            field = self.places_for_ship()
        return field

    def places_for_ship(self):  #Ставим корабли на поле
        length = [3, 2, 2, 1, 1, 1, 1]  #Создадим список, где переберем все длины кораблей и их количество
        field = Field(size=self.size) #Вызовем класс доски
        attempts = 0  #Счетчик попыток или ошибочно расставленных кораблей
        for i in length:  #Для каждого i-того элемента будем расставлять карабли
            while True:
                attempts += 1 #Прибавляем каждый раз при запуске цикла
                if attempts > 2000:  #Если попыток было больше 2000, то возвращаем None
                    return None
                ship = Ship(Point(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))  #Ставим рандомный корабль, передавая сначала данные в координаты, а затем в корабли
                try:
                    field.add_ship(ship) #Добавяем корабль на поле
                    break
                except FieldBadShipException: #Пропускаем ошибку неправильной постановки корабля
                    pass
        field.begin()
        return field

    def greet(self):
        print('Приветствуем вас в игре "Морской бой" \n Готовы сразиться с компьютером? Тогда начнем!')

    def game_main(self):
        num = 0  #Номер хода
        while True:
            print("_" * 20)
            print("Твоя доска выглядит так:")  #Вывод доски игрока
            print(self.gamer.field)
            print("_" * 20)
            print("Доска компьютера выглядит так")  #Вывод доски компьютера
            print(self.computer.field)
            if num % 2 == 0:  #Каждый четный ход - игрока
                print("_" * 20)
                print("Твой ход!")
                repeat = self.gamer.shoot_in_place()  #Возвращаем функцию выстрела
            else:
                print("_" * 20)  #Каждый нечетный ход - компьютера
                print("Ход компьютера!")
                repeat = self.computer.shoot_in_place()
            if repeat:
                num -= 1

            if self.computer.field.count == 7:  #Победа в случае убийства всех кораблей
                print("_" * 20)
                print("Ты выиграл!")
                break

            if self.gamer.field.count == 7:
                print("_" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.game_main()


g = Game()
g.start()