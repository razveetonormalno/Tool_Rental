from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from sqlite3 import IntegrityError
from datetime import datetime
import bd_editor

class AuthFrame(Tk):
    def __init__(self):
        super().__init__()
        self.bd = bd_editor.BD(True)
        self.title("Авторизация")
        self.geometry("300x300")
        self.configure(background="#323232")
        self.login_label = Label(text="Логин:", background="#323232", fg="white").pack()
        self.login = Entry(width=20)
        self.login.pack()
        self.password_login = Label(text="Пароль:", background="#323232", fg="white").pack()
        self.password = Entry(width=20)
        self.password.pack()
        self.style = ttk.Style()
        self.style.configure("TButton", background="#323232")
        self.button = Button(text="Авторизоваться", bg="yellow", command=self.auth)
        self.button.pack()

    def auth(self):
        if self.bd.login(self.login.get(), self.password.get()):
            self.destroy()
            messagebox.showinfo("Добро пожаловать!", 'Авторизация прошла успешно')
            app = MainFrame()
            app.mainloop()
        else:
            messagebox.showerror("Ошибка авторизации", 'Авторизация не прошла! Попробуйте ввести данные снова')

class MainFrame(Tk):
    def __init__(self):
        super().__init__()
        # self.iconbitmap("tool_building_construction_repair_maintenance_icon_229996.ico")
        self.geometry("1200x800")
        self.minsize(1175, 775)
        self.maxsize(1300, 900)
        self.title("Учёт Электроинструмента")
        self.bd = bd_editor.BD(False)
        self.check = False
        # self.configure(bg="#323232")

        self.frame_1 = Frame(self, bg="yellow")
        self.button_search = Button(self.frame_1, text="Поиск инструмента", bg="yellow", command=self.categories).grid(row=0, column=0)
        self.button_list = Button(self.frame_1, text="Список заказов", command=self.zakaz_list).grid(row=0, column=1)
        self.button_get_clients = Button(self.frame_1, text="Клиенты", command=self.clients).grid(row=0, column=2)
        self.button_get_employees = Button(self.frame_1, text="Сотрудники", command=self.emp_btn).grid(row=0, column=3)
        self.frame_1.pack()

    def close_list(self):
        self.tree2.destroy()
        self.scrollbar.destroy()

    def delete(self):
        """ Удаление таблицы """
        self.button_set_st_inst.destroy()
        self.notebook.destroy()
        self.button_close.destroy()
        self.scrollbar.destroy()

    def clear_window(self):
        """ Обновление экрана """
        # Закрывает список
        try:
            self.close_list()
        except AttributeError:
            pass

        # Закрывает кнопки в списке заказов
        try:
            self.del_rent.destroy()
            self.button_new.destroy()
            self.button_close_rent.destroy()
            self.button_search_order.destroy()
            self.frame_rent.destroy()
        except (AttributeError, TypeError):
            pass

        # Закрывает кнопки в списке клиентов
        try:
            self.del_client.destroy()
            self.add_client.destroy()
            self.button_search_client.destroy()
            self.frame_clients.destroy()
        except (AttributeError, TypeError):
            pass

        # Закрывает кнопки в списке сотрудников
        try:
            self.del_emp.destroy()
            self.add_emp.destroy()
            self.button_search_emp.destroy()
            self.frame_emp.destroy()
        except (AttributeError, TypeError):
            pass

        # Закрывает кнопки в списке инструментов
        try:
            self.button_del_inst.destroy()
            self.button_add_inst.destroy()
            self.button_search_inst.destroy()
            self.frame_categories.destroy()
            self.ch_st_w.destroy()
        except (AttributeError, TypeError):
            pass

        # Удаляет таблицу
        try:
            self.delete()
        except AttributeError:
            pass

        # Закрывает окна Toplevel
        try:
            self.new_w.destroy()
        except AttributeError:
            pass

    def table(self, frame, category, curs, filter_o):
        """ Создание таблицы и заполнение данными """
        s = ttk.Style()
        s.configure('Treeview', rowheight=80)
        self.tree = ttk.Treeview(frame, columns=("id", "Name", "Description", "Price", "Status"), show="headings",
                                 selectmode="extended", cursor=curs)
        self.scrollbar = ttk.Scrollbar(frame, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack()

        self.tree.heading("id", text="id", anchor=CENTER)
        self.tree.heading("Name", text="Наименование", anchor=CENTER)
        self.tree.heading("Description", text="Описание", anchor=CENTER)
        self.tree.heading("Price", text="Цена", anchor=CENTER)
        self.tree.heading("Status", text="Статус", anchor=CENTER)

        self.tree.column("#1", stretch=True, width=40, anchor=CENTER)
        self.tree.column("#2", stretch=True, width=200)
        self.tree.column("#3", stretch=True, width=300)
        self.tree.column("#4", stretch=True, width=150, anchor=CENTER)
        self.tree.column("#5", stretch=True, width=100)
        if curs == "arrow":
            if filter_o == "":
                for item in self.bd.search_(category, True):
                    self.tree.insert("", END, values=item)
                self.tree.bind('<<TreeviewSelect>>', self.items_selected)
            else:
                for item in self.bd.get_filter_instruments(category, filter_o):
                    self.tree.insert("", END, values=item)
                    self.tree.bind('<<TreeviewSelect>>', self.items_selected)
        elif curs == "plus":
            for item in self.bd.search_(category, False):
                self.tree.insert("", END, values=item)
            self.tree.bind('<<TreeviewSelect>>', self.items_selected)

        return self.tree

    def instrument_delete(self):
        result = messagebox.askyesno("Подтверждение",
                                     "Вы точно хотите удалить данный(-ые) инструмент(-ы)? \nДанное действие нельзя будет отменить!")
        if result:
            a = []
            for category in self.cat:
                for i in category.selection():
                    a.append(category.item(i)['values'][0])
            self.bd.inst_delete(a[0])
            messagebox.showinfo("Подтверждение", "Удаление выполнено")
            self.bd.connection.commit()
            self.categories()
        else:
            messagebox.showinfo("Подтверждение", "Удаление отменено")

    def inst_add(self):
        name_entry = self.name_inst.get().strip()
        description_entry = self.description.get().strip()
        if len(description_entry) < 150:
            if len(name_entry) < 35:
                if self.price_inst.get().isdigit():
                    self.bd.inst_add(self.cat_comb.get(), self.name_inst.get(), self.description.get(), self.price_inst.get())
                    messagebox.showinfo("Готово", "Новый инструмент добавлен")
                    self.new_w.destroy()
                    self.bd.connection.commit()
                    self.clear_window()
                    self.categories()
                else:
                    messagebox.showerror("Ошибка", "Цена должна состоять из цифр!!")
            else:
                messagebox.showerror("Ошибка", "Наименование должно содержать меньше 35 символов!")
        else:
            messagebox.showerror("Ошибка", "Описание должно содержать меньше 150 символов!")

    def instrument_add(self):
        self.new_w = Toplevel()
        self.new_w.geometry("300x300")
        category = ("Шуруповерты", "Электродрели", "Фены строительные", "Циркулярные пилы",
                    "Шлифовальные машины", "Строительные пылесосы", "Электролобзики")
        Label(self.new_w, text="Категория").pack()
        self.cat_comb = ttk.Combobox(self.new_w, values=category, width=20, state="readonly")
        self.cat_comb.pack()
        Label(self.new_w, text="Наименование").pack()
        self.name_inst = Entry(self.new_w, width=28, justify=CENTER)
        self.name_inst.pack()
        Label(self.new_w, text="Описание").pack()
        self.description = Entry(self.new_w, width=30)
        self.description.pack()
        Label(self.new_w, text="Цена").pack()
        self.price_inst = Entry(self.new_w, width=20)
        self.price_inst.pack()
        button_ok = Button(self.new_w, text="Подтвердить", command=self.inst_add)
        button_ok.pack()

    def search_inst(self):
        def srch_inst():
            self.categories(filter_o=self.filt_entry.get())
            self.new_w.destroy()

        self.new_w = Toplevel()
        self.new_w.geometry("300x100")
        Label(self.new_w, text="Фильтр").pack()
        self.filt_entry = Entry(self.new_w, width=20, justify=CENTER)
        self.filt_entry.pack()
        self.button_conf = Button(self.new_w, text="Найти", command=srch_inst)
        self.button_conf.pack()

    def categories(self, curs="arrow", filter_o=""):
        """ Кнопка <ПОИСК ИНСТРУМЕНТА>. Создание дерева с категориями """
        self.clear_window()
        self.frame_categories = ttk.Frame()
        self.button_set_st_inst = Button(self.frame_categories, text="Поменять статус инструмента", command=self.change_st_inst)
        self.button_set_st_inst.grid(row=0, column=0)
        self.button_del_inst = Button(self.frame_categories, text="Удалить инструмент", command=self.instrument_delete)
        self.button_del_inst.grid(row=0, column=1)
        self.button_add_inst = Button(self.frame_categories, text="Добавить", command=self.instrument_add)
        self.button_add_inst.grid(row=0, column=2)
        self.button_search_inst = Button(self.frame_categories, text="Поиск", command=self.search_inst)
        self.button_search_inst.grid(row=0, column=3)
        self.frame_categories.pack()

        self.notebook = ttk.Notebook()
        self.notebook.pack(fill=BOTH)

        frame1 = ttk.Frame(self.notebook)
        frame2 = ttk.Frame(self.notebook)
        frame3 = ttk.Frame(self.notebook)
        frame4 = ttk.Frame(self.notebook)
        frame5 = ttk.Frame(self.notebook)
        frame6 = ttk.Frame(self.notebook)
        frame7 = ttk.Frame(self.notebook)
        frames = (frame1, frame2, frame3, frame4, frame5, frame6, frame7)

        frame1.pack(fill=BOTH, expand=True)
        frame2.pack(fill=BOTH, expand=True)
        frame3.pack(fill=BOTH, expand=True)
        frame4.pack(fill=BOTH, expand=True)
        frame5.pack(fill=BOTH, expand=True)
        frame6.pack(fill=BOTH, expand=True)
        frame7.pack(fill=BOTH, expand=True)

        if curs != "arrow":
            self.btns = []
            for i in frames:
                temp = Button(i, text="Добавить", command=self.entr)
                temp.pack(anchor=CENTER)
                self.btns.append(temp)

        self.category = ("Шуруповерты", "Электродрели", "Фены строительные", "Циркулярные пилы", "Шлифовальные машины",
                         "Строительные пылесосы", "Электролобзики")
        self.notebook.add(frame1, text="Шуропеверты")
        self.tr_1 = self.table(frame1, self.category[0], curs, filter_o)
        self.tr_2 = self.table(frame2, self.category[1], curs, filter_o)
        self.tr_3 = self.table(frame3, self.category[2], curs, filter_o)
        self.tr_4 = self.table(frame4, self.category[3], curs, filter_o)
        self.tr_5 = self.table(frame5, self.category[4], curs, filter_o)
        self.tr_6 = self.table(frame6, self.category[5], curs, filter_o)
        self.tr_7 = self.table(frame7, self.category[6], curs, filter_o)

        self.cat = (self.tr_1, self.tr_2, self.tr_3, self.tr_4, self.tr_5, self.tr_6, self.tr_7)

        self.notebook.add(frame2, text="Электродрели")
        self.notebook.add(frame3, text="Строительные фены")
        self.notebook.add(frame4, text="Циркулярные пилы")
        self.notebook.add(frame5, text="Шлифовальные машины")
        self.notebook.add(frame6, text="Строительные пылесосы")
        self.notebook.add(frame7, text="Электролобзики")

    def rent_delete(self):
        result = messagebox.askyesno("Подтверждение", "Вы точно хотите удалить данный(-е) заказ(-ы)? \nДанное действие нельзя будет отменить")
        if result:
            id_rent = self.tree2.item(self.tree2.selection())['values'][0]
            self.bd.rent_delete(id_rent)
            messagebox.showinfo("Подтверждение", "Удаление выполнено")
            self.bd.connection.commit()
            self.zakaz_list()
        else:
            messagebox.showinfo("Подтверждение", "Удаление отменено")

    def search_order(self):
        def srch_order():
            self.zakaz_list(self.filt_entry.get())
            self.new_w.destroy()
        self.new_w = Toplevel()
        self.new_w.geometry("300x100")
        Label(self.new_w, text="Фильтр").pack()
        self.filt_entry = Entry(self.new_w, width=20, justify=CENTER)
        self.filt_entry.pack()
        self.button_conf = Button(self.new_w, text="Найти", command=srch_order)
        self.button_conf.pack()

    def zakaz_list(self, filter_o=""):
        self.clear_window()
        self.frame_rent = ttk.Frame()
        self.del_rent = Button(self.frame_rent, text="Удалить заказ", command=self.rent_delete)
        self.del_rent.grid(row=0, column=0)
        self.button_new = Button(self.frame_rent, text="Новый заказ", command=self.new_order)
        self.button_new.grid(row=0, column=1)
        self.button_close_rent = Button(self.frame_rent, text="Закрыть аренду", command=self.close_order)
        self.button_close_rent.grid(row=0, column=2)
        self.button_search_order = Button(self.frame_rent, text="Поиск", command=self.search_order)
        self.button_search_order.grid(row=0, column=3)
        self.frame_rent.pack()
        s = ttk.Style()
        s.configure('Treeview', rowheight=20)
        self.tree2 = ttk.Treeview(columns=("id", "Date", "Datex", "Price", "id_e", "id_c", "id_i", "Payment", "Status", "Pledge"),
                                  show="headings", selectmode="extended")
        self.scrollbar = ttk.Scrollbar(command=self.tree2.yview)
        self.tree2.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.tree2.pack()

        self.tree2.heading("id", text="id")
        self.tree2.heading("Date", text="Дата аренды")
        self.tree2.heading("Datex", text="Дата возврата")
        self.tree2.heading("Price", text="Цена")
        self.tree2.heading("id_e", text="id Сотрудника")
        self.tree2.heading("id_c", text="id Клиента")
        self.tree2.heading("id_i", text="id Инструмента")
        self.tree2.heading("Payment", text="Вид оплаты")
        self.tree2.heading("Status", text="Статус")
        self.tree2.heading("Pledge", text="Залог")

        self.tree2.column("id", width=25, anchor=CENTER)
        self.tree2.column("id_e", width=220)
        self.tree2.column("id_c", width=220)
        self.tree2.column("id_i", width=100, anchor=CENTER)
        self.tree2.column("Price", width=70, anchor=CENTER)
        self.tree2.column("Date", stretch=True, width=90, anchor=CENTER)
        self.tree2.column("Datex", stretch=True, width=90, anchor=CENTER)
        self.tree2.column("Price", stretch=True, width=70, anchor=CENTER)
        self.tree2.column("Payment", stretch=True, width=100, anchor=CENTER)
        self.tree2.column("Status", stretch=True, width=70, anchor=CENTER)
        self.tree2.column("Pledge", stretch=True, width=70, anchor=CENTER)

        if filter_o == "":
            for item in self.bd.get_all_rents():
                self.tree2.insert("", END, values=item)
            self.tree2.bind('<<TreeviewSelect>>', self.items_selected)
        else:
            filtered_rents = self.bd.get_filter_rents(filter_o)
            if filtered_rents:
                for item in filtered_rents:
                    self.tree2.insert("", END, values=item)
                self.tree2.bind('<<TreeviewSelect>>', self.items_selected)
            else:
                # messagebox.showinfo("Ошибка", "Такой информации в таблице не найдено!")
                self.zakaz_list()

    def blocked(self, event):
        self.phone_entry['state'] = "normal"
        telephone = self.bd.get_telephone(self.FIO.get())
        self.phone_entry.delete(0, END)
        self.phone_entry.insert(0, telephone)
        self.phone_entry['state'] = "disabled"

    def confirm(self):
        messagebox.showinfo("Готово", "Создан новый заказ")
        self.new_w.destroy()
        self.bd.connection.commit()
        self.clear_window()
        self.zakaz_list()

    def items_selected(self, event):
        pass

    def entr(self):
        """ Обработчик нажатия на <Enter> для добавления инструмента"""
        a = []
        for category in self.cat:
            for i in category.selection():
                a.append(category.item(i)['values'][0])
        print(tuple(a))
        self.id_entry.configure(state=NORMAL)
        self.id_entry.delete(0, END)
        self.id_entry.insert(0, str(a)[1:-1])
        self.id_entry.configure(state=DISABLED)

    def cls(self, event):
        for i in self.btns:
            i.pack_forget()

    def new_order(self):
        self.categories("plus")
        self.new_w = Toplevel()
        self.new_w.geometry("300x500")
        Label(self.new_w, text="id").pack()
        self.id_entry = Entry(self.new_w, width=20, state=DISABLED)
        self.id_entry.pack()
        Label(self.new_w, text="ФИО").pack()
        a = tuple(i[0] for i in self.bd.get_fio_clients())
        self.FIO = ttk.Combobox(self.new_w, values=a)
        self.FIO.pack()
        self.FIO.bind("<<ComboboxSelected>>", self.blocked)
        Label(self.new_w, text="Телефон").pack()
        self.phone_entry = Entry(self.new_w, width=15)
        self.phone_entry.pack()
        Label(self.new_w, text="Залог").pack()
        self.zalog_entry = Entry(self.new_w, width=10)
        self.zalog_entry.pack()
        Label(self.new_w, text="Дата Аренды").pack()
        self.da_entry = Entry(self.new_w, width=10)
        self.da_entry.pack()
        Label(self.new_w, text="Дата Возврата").pack()
        self.dv_entry = Entry(self.new_w, width=10)
        self.dv_entry.pack()
        Label(self.new_w, text="Вид оплаты").pack()
        self.oplata = ttk.Combobox(self.new_w, values=["Наличные", "Карта"], state="readonly")
        self.oplata.pack()
        Label(self.new_w, text="Итог").pack()
        self.price_entry = Entry(self.new_w, state=DISABLED)
        self.price_entry.pack()
        button_price = Button(self.new_w, text="Расчёт", command=self.count).pack()
        self.button_ok = Button(self.new_w, text="Подтвердить", command=self.confirm)
        self.new_w.bind("<Destroy>", self.cls)

    def count(self):
        fio_entry = self.FIO.get().strip()
        phone_entry = self.phone_entry.get().strip()
        pledge_entry = self.zalog_entry.get().strip()
        date = self.da_entry.get().strip()
        date_ex = self.dv_entry.get().strip()
        # Проверка телефона
        if len(phone_entry) == 16:
            if phone_entry[0] == "+" and phone_entry[2] == "(" and phone_entry[6] == ")" and phone_entry[10] == "-" \
                    and phone_entry[13] == "-":
                for sym in phone_entry.replace('+', '').replace('(', '').replace(')', '').replace('-', ''):
                    if not sym.isdigit():
                        messagebox.showinfo("Ошибка", "В номере телефона не должно быть букв!")
                        return
            else:
                messagebox.showinfo("Ошибка", "Поле ввода телефона не соответствует формату '+7(XXX)XXX-XX-XX'!")
                return
        else:
            messagebox.showinfo("Ошибка", "В номере телефона должно быть 16 символов! Формат: +7(XXX)XXX-XX-XX")
            return
        # Проверка даты
        if len(date) == 10 and len(date_ex):
            if date[2] == "." and date[5] == "." and date_ex[2] == "." and date_ex[5] == ".":
                try:
                    diff = datetime.strptime(date_ex, "%d.%m.%Y") - datetime.strptime(date, "%d.%m.%Y")
                    if diff.days < 1 or int(date[6:]) != 2023 or 2023 > int(date_ex[6:]) or int(date_ex[6:]) > 2024:
                        raise ValueError
                except ValueError:
                    messagebox.showinfo("Ошибка", "Введите корректную дату!")
                    return
                for i in date.replace('.', ''):
                    if not i.isdigit():
                        messagebox.showinfo("Ошибка", "Дата должна состоять из цифр!")
                        return
                for i in date_ex.replace('.', ''):
                    if not i.isdigit():
                        messagebox.showinfo("Ошибка", "Дата должна состоять из цифр!")
                        return
            else:
                messagebox.showinfo("Ошибка", "Дата должна быть формата XX.XX.XXXX!")
                return
        else:
            messagebox.showinfo("Ошибка", "Дата должна содержать 10 символов!")
            return

        if len(fio_entry.split()) == 3:
            if pledge_entry.isdigit():
                try:
                    self.bd.add_client((self.FIO.get(), self.phone_entry.get()))
                    self.price_entry.configure(state=NORMAL)
                    self.price_entry.delete(0, END)
                    self.price_entry.insert(0, self.bd.add_rent((self.da_entry.get(), self.dv_entry.get(), self.id_entry.get(),
                                                                 self.oplata.get(), self.zalog_entry.get())))
                    self.price_entry.configure(state=DISABLED)
                    self.button_ok.pack()
                except Exception as e:
                    raise
                    messagebox.showerror("ERROR", "Упс... Что-то пошло не так")
                    self.new_w.destroy()
                    self.new_order()
            else:
                messagebox.showinfo("Ошибка", "Залог должен состоять из цифр!")
                return
        else:
            messagebox.showinfo("Ошибка", "ФИО должно состоять из 3 слов!")
            return

    def confirm_cl(self):
        messagebox.showinfo("Готово", "Аренда закрыта")
        self.bd.set_rent_status(self.id_order.get())
        self.cl_or_w.destroy()
        self.bd.connection.commit()
        self.clear_window()
        self.zakaz_list()

    def close_order(self):
        self.cl_or_w = Toplevel()
        self.cl_or_w.geometry("300x150")
        Label(self.cl_or_w, text="Выберите заказ").pack()
        a = self.bd.get_id_rents()
        self.id_order = ttk.Combobox(self.cl_or_w, values=a, state="readonly")
        self.id_order.pack()

        Button(self.cl_or_w, text="Подтвердить", command=self.confirm_cl).pack()

    def confirm_st(self):
        messagebox.showinfo("Готово", "Статус изменен")
        self.bd.set_instrument_status(self.id_instruments.get(), self.statuses.get())
        self.ch_st_w.destroy()
        self.bd.connection.commit()
        self.clear_window()
        self.categories()

    def change_st_inst(self):
        self.ch_st_w = Toplevel()
        self.ch_st_w.geometry("300x150")
        Label(self.ch_st_w, text="Выберите инструмент").pack()
        a = self.bd.get_id_instruments()
        self.id_instruments = ttk.Combobox(self.ch_st_w, values=a, state="readonly")
        self.id_instruments.pack()
        self.statuses = ttk.Combobox(self.ch_st_w, values=("На проверке", "Готов", "В ремонте", "Сломан"), state="readonly")
        self.statuses.pack()

        Button(self.ch_st_w, text="Подтвердить", command=self.confirm_st).pack()

    def client_delete(self):
        result = messagebox.askyesno("Подтверждение", "Вы точно хотите удалить данного(-ых) клиента(-ов)? \nДанное действие нельзя будет отменить!")
        if result:
            id_client = self.tree2.item(self.tree2.selection())['values'][0]

            self.bd.client_delete(id_client)
            messagebox.showinfo("Подтверждение", "Удаление выполнено")
            self.bd.connection.commit()
            self.clients()
        else:
            messagebox.showinfo("Подтверждение", "Удаление отменено")

    def confirm_add(self):
        FIO_entry = self.FIO.get().strip()
        phone_entry = self.phone_entry.get().strip()
        if len(phone_entry) == 16:
            if phone_entry[0] == "+" and phone_entry[2] == "(" and phone_entry[6] == ")" and phone_entry[10] == "-" \
               and phone_entry[13] == "-":
                for sym in phone_entry.replace('+', '').replace('(', '').replace(')', '').replace('-', ''):
                    if not sym.isdigit():
                        messagebox.showinfo("Ошибка", "В номере телефона не должно быть букв!")
                        return
            else:
                messagebox.showinfo("Ошибка", "Поле ввода телефона не соответствует формату '+7(XXX)XXX-XX-XX'!")
                return
        else:
            messagebox.showinfo("Ошибка", "В номере телефона должно быть 16 символов! Формат: +7(XXX)XXX-XX-XX")
            return

        if len(FIO_entry.split()) == 3:
            self.bd.client_add(FIO_entry, phone_entry)
        else:
            messagebox.showinfo("Ошибка", "Поле ввода ФИО должно состоять из 3 слов!")
            return
        messagebox.showinfo("Готово", "Новый клиент добавлен")
        self.new_w.destroy()
        self.bd.connection.commit()
        self.clear_window()
        self.clients()

    def client_add(self):
        self.new_w = Toplevel()
        self.new_w.geometry("300x150")
        Label(self.new_w, text="ФИО").pack()
        self.FIO = Entry(self.new_w, width=28, justify=CENTER)
        self.FIO.pack()
        Label(self.new_w, text="Телефон").pack()
        self.phone_entry = Entry(self.new_w, width=20)
        self.phone_entry.pack()
        button_ok = Button(self.new_w, text="Подтвердить", command=self.confirm_add)
        button_ok.pack()

    def search_client(self):
        def srch_client():
            self.clients(self.filt_entry.get())
            self.new_w.destroy()
        self.new_w = Toplevel()
        self.new_w.geometry("300x200")
        Label(self.new_w, text="Фильтр").pack()
        self.filt_entry = Entry(self.new_w, width=20, justify=CENTER)
        self.filt_entry.pack()
        self.button_conf = Button(self.new_w, text="Найти", command=srch_client)
        self.button_conf.pack()

    def clients(self, filter_o=""):
        self.clear_window()
        self.frame_clients = ttk.Frame()
        self.del_client = Button(self.frame_clients, text="Удалить клиента", command=self.client_delete)
        self.del_client.grid(row=0, column=0)
        self.add_client = Button(self.frame_clients, text="Добавить клиента", command=self.client_add)
        self.add_client.grid(row=0, column=1)
        self.button_search_client = Button(self.frame_clients, text="Поиск", command=self.search_client)
        self.button_search_client.grid(row=0, column=2)
        self.frame_clients.pack()
        s = ttk.Style()
        s.configure('Treeview', rowheight=20)
        self.tree2 = ttk.Treeview(columns=("id", "FIO", "Phone"), show="headings")
        self.scrollbar = ttk.Scrollbar(command=self.tree2.yview)
        self.tree2.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.tree2.pack()

        self.tree2.heading("id", text="id")
        self.tree2.heading("FIO", text="ФИО")
        self.tree2.heading("Phone", text="Телефон")

        self.tree2.column("id", width=75, anchor=CENTER)
        self.tree2.column("FIO", width=400, anchor=CENTER)
        self.tree2.column("Phone", width=300, anchor=CENTER)

        if filter_o == "":
            for item in self.bd.get_all_clients():
                self.tree2.insert("", END, values=item)
        else:
            filtered_clients = self.bd.get_filter_clients(filter_o)
            if filtered_clients:
                for item in filtered_clients:
                    self.tree2.insert("", END, values=item)
                self.tree2.bind('<<TreeviewSelect>>', self.items_selected)
            else:
                # messagebox.showinfo("Ошибка", "Такой информации в таблице не найдено!")
                self.clients()

    def emp_delete(self):
        result = messagebox.askyesno("Подтверждение",
                                     "Вы точно хотите удалить данного(-ых) клиента(-ов)? \nДанное действие нельзя будет отменить!")
        if result:
            id_employee = self.tree2.item(self.tree2.selection())['values'][0]
            self.bd.employee_delete(id_employee)
            messagebox.showinfo("Подтверждение", "Удаление выполнено")
            self.bd.connection.commit()
            self.employees()
        else:
            messagebox.showinfo("Подтверждение", "Удаление отменено")

    def emp_add(self):
        fio_entry = self.FIO.get().strip()
        password = self.password_entry.get().strip()
        phone_entry = self.phone_entry.get().strip()
        if len(phone_entry) == 16:
            if phone_entry[0] == "+" and phone_entry[2] == "(" and phone_entry[6] == ")" and phone_entry[10] == "-" \
               and phone_entry[13] == "-":
                for sym in phone_entry.replace('+', '').replace('(', '').replace(')', '').replace('-', ''):
                    if not sym.isdigit():
                        messagebox.showinfo("Ошибка", "В номере телефона не должно быть букв!")
                        return
            else:
                messagebox.showinfo("Ошибка", "Поле ввода телефона не соответствует формату '+7(XXX)XXX-XX-XX'!")
                return
        else:
            messagebox.showinfo("Ошибка", "В номере телефона должно быть 16 символов! Формат: +7(XXX)XXX-XX-XX")
            return

        if len(fio_entry.split()) == 3:
            if len(password) < 18:
                try:
                    self.bd.employee_add(fio_entry, self.login_entry.get(), password, phone_entry)
                except IntegrityError as e:
                    messagebox.showinfo("Ошибка", "Такой логин уже используется!")
                    print(e)
                    return
            else:
                messagebox.showinfo("Ошибка", "Пароль не должен превышать 18 символов!")
                return
        else:
            messagebox.showinfo("Ошибка", "Поле ввода ФИО должно состоять из 3 слов!")
            return
        messagebox.showinfo("Готово", "Новый сотрудник добавлен")
        self.new_w.destroy()
        self.bd.connection.commit()
        self.clear_window()
        self.employees()

    def employee_add(self):
        self.new_w = Toplevel()
        self.new_w.geometry("300x300")
        Label(self.new_w, text="ФИО").pack()
        self.FIO = Entry(self.new_w, width=28, justify=CENTER)
        self.FIO.pack()
        Label(self.new_w, text="Логин").pack()
        self.login_entry = Entry(self.new_w, width=20)
        self.login_entry.pack()
        Label(self.new_w, text="Пароль").pack()
        self.password_entry = Entry(self.new_w, width=20)
        self.password_entry.pack()
        Label(self.new_w, text="Телефон").pack()
        self.phone_entry = Entry(self.new_w, width=20)
        self.phone_entry.pack()
        button_ok = Button(self.new_w, text="Подтвердить", command=self.emp_add)
        button_ok.pack()

    def search_employee(self):
        def srch_employee():
            self.employees(self.filt_entry.get())
            self.new_w.destroy()
        self.new_w = Toplevel()
        self.new_w.geometry("300x200")
        Label(self.new_w, text="Фильтр").pack()
        self.filt_entry = Entry(self.new_w, width=20, justify=CENTER)
        self.filt_entry.pack()
        self.button_conf = Button(self.new_w, text="Найти", command=srch_employee)
        self.button_conf.pack()

    def emp_btn(self):
        if not self.check:
            def check_code():
                if self.code.get() == "54321":
                    messagebox.showinfo("Готово", "Вход разрешен!")
                    self.check = True
                    self.employees()
                else:
                    messagebox.showinfo("Готово", "Неверный пароль!")
            self.new_w = Toplevel()
            self.new_w.geometry("300x100")
            Label(self.new_w, text="Пароль").pack()
            self.code = Entry(self.new_w, width=28, justify=CENTER)
            self.code.pack()
            but_cat = Button(self.new_w, text="Вход", command=check_code)
            but_cat.pack()
        else:
            self.employees()

    def employees(self, filter_o=""):
        self.clear_window()
        self.frame_emp = ttk.Frame()
        self.del_emp = Button(self.frame_emp, text="Удалить сотрудника", command=self.emp_delete)
        self.del_emp.grid(row=0, column=0)
        self.add_emp = Button(self.frame_emp, text="Добавить сотрудника", command=self.employee_add)
        self.add_emp.grid(row=0, column=1)
        self.button_search_emp = Button(self.frame_emp, text="Поиск", command=self.search_employee)
        self.button_search_emp.grid(row=0, column=2)
        self.frame_emp.pack()
        s = ttk.Style()
        s.configure('Treeview', rowheight=20)
        self.tree2 = ttk.Treeview(columns=("id", "FIO", "Login", "Password", "Phone"), show="headings")
        self.scrollbar = ttk.Scrollbar(command=self.tree2.yview)
        self.tree2.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.tree2.pack()

        self.tree2.heading("id", text="id")
        self.tree2.heading("FIO", text="ФИО")
        self.tree2.heading("Login", text="Логин")
        self.tree2.heading("Password", text="Пароль")
        self.tree2.heading("Phone", text="Телефон")

        self.tree2.column("id", width=75, anchor=CENTER)
        self.tree2.column("FIO", width=400, anchor=CENTER)
        self.tree2.column("Login", width=300, anchor=CENTER)
        self.tree2.column("Password", width=200, anchor=CENTER)
        self.tree2.column("Phone", width=200, anchor=CENTER)

        if filter_o == "":
            for item in self.bd.get_all_employees():
                self.tree2.insert("", END, values=item)
        else:
            filtered_employees = self.bd.get_filter_employees(filter_o)
            if filtered_employees:
                for item in filtered_employees:
                    self.tree2.insert("", END, values=item)
                self.tree2.bind('<<TreeviewSelect>>', self.items_selected)
            else:
                # messagebox.showinfo("Ошибка", "Такой информации в таблице не найдено!")
                self.employees()

auth = AuthFrame()
auth.mainloop()