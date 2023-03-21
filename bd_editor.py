import sqlite3
from datetime import datetime

class BD:
    def __init__(self, check):
        self.db_name = "Прокат_Инструментов.db"
        if check:
            self.user_id = -1
        else:
            with open('cfg.txt', 'r') as file:
                u = f'{file.read()}'
            self.user_id = u
        self.client_id = -1
        self.price = -1
        self.connection = sqlite3.connect(self.db_name)
        self.cursorObj = self.connection.cursor()
        self.cursorObj.execute("PRAGMA journal_mode=WAL")

    def login(self, __login__, __password__):
        """ Функция проверки логина и пароля """
        employees = self.cursorObj.execute("SELECT id, Login, Password FROM Employees")
        for item in employees:
            if item[1] == __login__.strip() and item[2] == __password__.strip():
                self.user_id = item[0]
                with open('cfg.txt', 'w') as file:
                    print(f"{self.user_id}", file=file)
                return True
            else:
                continue
        return False

    def add_client(self, __client_data__):
        """ Добавление клиента"""
        check = self.cursorObj.execute("SELECT EXISTS(SELECT id FROM Client WHERE Phone = ?)",
                                       (__client_data__[1],)).fetchall()
        check = check[0][0]
        if not check:
            self.cursorObj.execute("INSERT INTO Client (FIO, Phone) VALUES (?, ?)", __client_data__)
            client = self.cursorObj.execute("SELECT id FROM Client WHERE Phone = ?", (__client_data__[1],)).fetchall()
            self.client_id = client[0][0]
        else:
            client = self.cursorObj.execute("SELECT id FROM Client WHERE Phone = ?", (__client_data__[1],)).fetchall()
            self.client_id = client[0][0]

    def add_rent(self, __rent_data__):
        """ Создание нового заказа """
        d1 = datetime.strptime(__rent_data__[1], "%d.%m.%Y")
        d2 = datetime.strptime(__rent_data__[0], "%d.%m.%Y")
        d3 = d1 - d2

        ids = f"({__rent_data__[2]})"
        price = self.cursorObj.execute(f"SELECT SUM(Price * {d3.days}) FROM Instruments WHERE id IN {ids}").fetchone()[0]

        self.cursorObj.execute("INSERT INTO Rent (Date, Date_Ex, Price, id_E, id_C, id_I, Payment, Status, Pledge) VALUES \
                                (?, ?, ?, ?, ?, ?, ?, ?, ?)", (__rent_data__[0], __rent_data__[1], str(price),
                                                               str(self.user_id), str(self.client_id), __rent_data__[2],
                                                               __rent_data__[3], "Открыт", __rent_data__[4]))
        self.cursorObj.execute(f"UPDATE Instruments SET Status=? WHERE id IN {ids}", ("Используется",))
        return price

    def get_fio_clients(self):
        """ Достать ФИО клиента """
        return self.cursorObj.execute("SELECT FIO FROM Client")

    # def get_fio_employees(self):
    #     """ Достать ФИО сотрудника """
    #     return self.cursorObj.execute("SELECT FIO FROM Employees")

    def get_telephone(self, __fio__):
        """ Достать телефон клиента """
        telephone = self.cursorObj.execute("SELECT Phone FROM Client WHERE FIO=?", (__fio__,)).fetchall()
        return telephone[0][0]

    def get_all_clients(self):
        """Список всех клиентов"""
        return self.cursorObj.execute("SELECT * FROM Client").fetchall()

    def get_all_employees(self):
        return self.cursorObj.execute("SELECT * FROM Employees").fetchall()

    def get_all_rents(self):
        """ Достать все заказы """
        arr_rents = self.cursorObj.execute("SELECT * FROM Rent").fetchall()
        arr_copy = list()
        for item in arr_rents:
            ls = list(item)
            fio_emp = self.cursorObj.execute("SELECT FIO FROM Employees WHERE id=?", (item[4],)).fetchall()
            fio_cl = self.cursorObj.execute("SELECT FIO FROM Client WHERE id=?", (item[5],)).fetchall()
            try:
                ls[4] = f"{ls[4]}, {fio_emp[0][0]}"
            except IndexError:
                ls[4] = f"{ls[4]}, DELETED"

            try:
                ls[5] = f"{ls[5]}, {fio_cl[0][0]}"
            except IndexError:
                ls[5] = f"{ls[5]}, DELETED"
            arr_copy.append(tuple(ls))
        return arr_copy

    def get_id_instruments(self):
        """ Достать id инструмента """
        arr = self.cursorObj.execute("SELECT id FROM Instruments").fetchall()
        arr_copy = list()
        for item in arr:
            arr_copy.append(item[0])
        return tuple(arr_copy)

    def get_id_rents(self):
        """ Достать id заказа """
        arr_ids = self.cursorObj.execute("SELECT id FROM Rent").fetchall()
        arr_copy = list()
        for item in arr_ids:
            status = self.cursorObj.execute("SELECT Status FROM Rent WHERE id=?", (item[0],)).fetchall()
            if status[0][0] == "Открыт":
                arr_copy.append(item[0])
        return tuple(arr_copy)

    def set_rent_status(self, __id_r__):
        """ Установить статус заказа как (Закрыт) и инструмента как (На проверке) """
        id_I = self.cursorObj.execute("SELECT id_I FROM Rent WHERE id=?", (__id_r__,)).fetchone()
        id_I = id_I.split(',')
        id_I = tuple(map(lambda x: x.strip(), id_I))
        self.cursorObj.execute("UPDATE Rent SET Status=? WHERE id=?", ("Закрыт", __id_r__))
        for i in id_I:
            self.cursorObj.execute("UPDATE Instruments SET Status=? WHERE id=?", ("На проверке", i))

    def set_instrument_status(self, __id_i__, __status__):
        """ Установить статус инструмента как (__status__) """
        self.cursorObj.execute("UPDATE Instruments SET Status=? WHERE id=?", (__status__, __id_i__))

    def search(self, __id_category__):
        """ Достать все инструменты по категории __id_category__ """
        ls = self.cursorObj.execute(
            "SELECT id, Name, Description, Price, Status FROM Instruments WHERE id_Category = ?", __id_category__)
        return ls

    def search_(self, __name_category__, __filter__):
        """Достать все инструменты по категории __name_category__"""
        if __filter__:
            ls = self.cursorObj.execute("SELECT id, Name, Description, Price, Status FROM Instruments WHERE Category=?",
                                        (__name_category__,))
        else:
            ls = self.cursorObj.execute("SELECT id, Name, Description, Price, Status FROM Instruments WHERE Category=? AND Status='Готов'",
                                        (__name_category__,))
        return ls

    def rent_delete(self, __id_rent__):
        self.cursorObj.execute("DELETE FROM Rent WHERE id = ?", (__id_rent__,))

    def client_delete(self, __id_client__):
        self.cursorObj.execute("DELETE FROM Client WHERE id = ?", (__id_client__,))

    def client_add(self, __fio__, __phone__):
        self.cursorObj.execute("INSERT INTO Client (FIO, Phone) VALUES (?, ?)", (__fio__, __phone__))

    def employee_add(self, __fio__, __login__, __password__, __phone__):
        self.cursorObj.execute("INSERT INTO Employees (FIO, Login, Password, Phone) VALUES (?, ?, ?, ?)",
                               (__fio__, __login__, __password__, __phone__))

    def employee_delete(self, __id_employee__):
        self.cursorObj.execute("DELETE FROM Employees WHERE id = ?", (__id_employee__,))

    def inst_delete(self, __id_instrument__):
        self.cursorObj.execute("DELETE FROM Instruments WHERE id = ?", (__id_instrument__,))

    def inst_add(self, __category__, __name__, __description__, __price__):
        self.cursorObj.execute("INSERT INTO Instruments (Category, Name, Description, Price) VALUES (?, ?, ?, ?)",
                               (__category__, __name__, __description__, __price__))

    def get_filter_rents(self, __filter__):
        request = f"SELECT * FROM Rent WHERE (id LIKE '%{__filter__}%'\n" \
                  f"OR Date LIKE '%{__filter__}%'\nOR Date_ex LIKE '%{__filter__}%'\nOR Price LIKE '%{__filter__}%'\n" \
                  f"OR id_E LIKE '%{__filter__}%'\nOR id_C LIKE '%{__filter__}%'\nOR id_I LIKE '%{__filter__}%'\n" \
                  f"OR Payment LIKE '%{__filter__}%'\nOR Status LIKE '%{__filter__}%'\nOR Pledge LIKE '%{__filter__}%')"
        arr = self.cursorObj.execute(request).fetchall()
        arr_copy = list()
        for item in arr:
            ls = list(item)
            fio_emp = self.cursorObj.execute("SELECT FIO FROM Employees WHERE id=?", (item[4],)).fetchall()
            fio_cl = self.cursorObj.execute("SELECT FIO FROM Client WHERE id=?", (item[5],)).fetchall()
            ls[4] = f"{ls[4]}, {fio_emp[0][0]}"
            ls[5] = f"{ls[5]}, {fio_cl[0][0]}"
            arr_copy.append(tuple(ls))
        return arr_copy

    def get_filter_clients(self, __filter__):
        request = f"SELECT * FROM Client WHERE (id LIKE '%{__filter__}%'\n" \
                  f"OR FIO LIKE '%{__filter__}%'\nOR Phone LIKE '%{__filter__}%')"
        arr = self.cursorObj.execute(request).fetchall()
        return arr

    def get_filter_employees(self, __filter__):
        request = f"SELECT * FROM Employees WHERE (id LIKE '%{__filter__}%'\n" \
                  f"OR FIO LIKE '%{__filter__}%'\nOR Login LIKE '%{__filter__}%'\nOR Password LIKE '%{__filter__}%')\n" \
                  f"OR Phone LIKE '%{__filter__}%'"
        arr = self.cursorObj.execute(request).fetchall()
        return arr

    def get_filter_instruments(self, __name_category__, __filter__):
        request = f"SELECT id, Name, Description, Price, Status FROM Instruments WHERE (id LIKE '%{__filter__}%'\n" \
                  f"OR Name LIKE '%{__filter__}%'\nOR Description LIKE '%{__filter__}%')\n" \
                  f"OR Price LIKE '%{__filter__}%'\nOR Status LIKE '%{__filter__}%'"
        arr = self.cursorObj.execute(request).fetchall()
        return arr

# if __name__ == '__main__':
    # login = input("Введите логин: ")
    # password = input("Введите пароль: ")
    # bd = BD(True)
    # for item in bd
    # print(tuple(bd.get_fio_clients()))
    # print(bd.login(login, password))
    # print(bd.get_all_instruments())

    # FIO = input("ДОБАВЛЕНИЕ КЛИЕНТА В БД\nВведите ФИО клиента: ")
    # Phone = input("Введите телефон: ")
    # Pledge = input("Введите залог: ")
    # print(bd.get_all_clients())
    # bd.add_client(FIO, Phone, Pledge)
    # print(bd.get_all_clients())
    #
    # rent_data = tuple(input("Введите данные аренды: ").split())
    # bd.add_rent(rent_data)
    #
    # print(from_db_cursor(bd.cursorObj.execute("SELECT * FROM Rent")))
    # id_cat = input("Введите категорию товара: ")
    # bd.search(id_cat)
