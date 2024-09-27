import tkinter as tk
from tkinter import messagebox
from ui.main_window import MainWindow
from database import Database


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.root.title("Авторизация")
        self.root.geometry("300x150")

        # Создание виджетов
        self.label_login = tk.Label(root, text="Логин:")
        self.label_login.pack()

        self.entry_login = tk.Entry(root)
        self.entry_login.pack()

        self.label_password = tk.Label(root, text="Пароль:")
        self.label_password.pack()

        self.entry_password = tk.Entry(root, show="*")
        self.entry_password.pack()

        self.button_login = tk.Button(root, text="Войти", command=self.login)
        self.button_login.pack()

    def login(self):
        # Получение данных из полей ввода
        login = self.entry_login.get()
        password = self.entry_password.get()

        # Подключение к базе данных
        user = self.db.execute_query(f"SELECT \"User\".user_id, Role.name, \"User\".name, \"User\".login, \"User\".password FROM \"User\" \
            JOIN Role ON \"User\".role_id = Role.role_id  \
            WHERE login = '{login}' and password = '{password}'")

        if user:
            messagebox.showinfo("Успех", "Авторизация прошла успешно!")
            self.root.destroy()  # Закрываем окно авторизации
            self.open_main_window(user)  # Открываем главное окно
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def open_main_window(self, user_info):
        root = tk.Tk()
        from ui.main_window import MainWindow  # Импортируем здесь, чтобы избежать циклического импорта
        app = MainWindow(root, user_info)
        root.mainloop()