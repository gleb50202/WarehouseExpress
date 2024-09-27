import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class AdministrationWindow:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.window = tk.Toplevel(self.root)
        self.window.title("Администрирование")
        self.window.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Администрирование", font=("Arial", 18)).pack(pady=20)

        # Создаем таблицу для отображения данных пользователей
        self.tree = ttk.Treeview(self.window, columns=(
            "user_id", "name", "role", "login", "password"), show="headings")

        # Определяем заголовки столбцов
        self.tree.heading("user_id", text="ID пользователя")
        self.tree.heading("name", text="Имя")
        self.tree.heading("role", text="Роль")
        self.tree.heading("login", text="Логин")
        self.tree.heading("password", text="Пароль")

        # Устанавливаем ширину столбцов
        self.tree.column("user_id", width=100)
        self.tree.column("name", width=150)
        self.tree.column("role", width=100)
        self.tree.column("login", width=100)
        self.tree.column("password", width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_users()

        tk.Button(self.window, text="Добавить пользователя", command=self.add_user).pack(pady=10)
        tk.Button(self.window, text="Редактировать пользователя", command=self.edit_user).pack(pady=10)
        tk.Button(self.window, text="Удалить пользователя", command=self.delete_user).pack(pady=10)

    def load_users(self):
        # Очищаем таблицу
        for i in self.tree.get_children():
            self.tree.delete(i)

        query = """
        SELECT
            u.user_id AS "UserID",
            u.name AS "Name",
            r.name AS "Role",
            u.login AS "Login",
            u.password AS "Password"
        FROM "User" u
        JOIN Role r ON u.role_id = r.role_id;
        """

        # Загружаем данные пользователей из базы данных
        users = self.db.execute_query(query)
        for user in users:
            self.tree.insert("", "end", values=user)

    def add_user(self):
        # Создаем диалоговое окно для добавления пользователя
        add_window = tk.Toplevel(self.window)
        add_window.title("Добавить пользователя")
        add_window.geometry("400x300")

        tk.Label(add_window, text="Имя:").pack(pady=5)
        name_entry = tk.Entry(add_window)
        name_entry.pack(pady=5)

        tk.Label(add_window, text="Роль:").pack(pady=5)
        role_entry = tk.Entry(add_window)
        role_entry.pack(pady=5)

        tk.Label(add_window, text="Логин:").pack(pady=5)
        login_entry = tk.Entry(add_window)
        login_entry.pack(pady=5)

        tk.Label(add_window, text="Пароль:").pack(pady=5)
        password_entry = tk.Entry(add_window)
        password_entry.pack(pady=5)

        def save_user():
            name = name_entry.get()
            role = role_entry.get()
            login = login_entry.get()
            password = password_entry.get()

            if not name or not role or not login or not password:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            # Получаем role_id по имени роли
            role_id = self.db.execute_query("SELECT role_id FROM Role WHERE name = %s", (role,))
            if not role_id:
                messagebox.showerror("Ошибка", "Роль не найдена")
                return

            self.db.execute_query(
                "INSERT INTO \"User\" (name, role_id, login, password) VALUES (%s, %s, %s, %s)",
                (name, role_id[0][0], login, password), fetch=False)
            add_window.destroy()
            self.load_users()

        tk.Button(add_window, text="Сохранить", command=save_user).pack(pady=10)

    def edit_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите пользователя для редактирования")
            return

        user_id = self.tree.item(selected_item)['values'][0]
        name = self.tree.item(selected_item)['values'][1]
        role = self.tree.item(selected_item)['values'][2]
        login = self.tree.item(selected_item)['values'][3]
        password = self.tree.item(selected_item)['values'][4]

        # Создаем диалоговое окно для редактирования пользователя
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Редактировать пользователя")
        edit_window.geometry("400x300")

        tk.Label(edit_window, text="Имя:").pack(pady=5)
        name_entry = tk.Entry(edit_window)
        name_entry.insert(0, name)
        name_entry.pack(pady=5)

        tk.Label(edit_window, text="Роль:").pack(pady=5)
        role_entry = tk.Entry(edit_window)
        role_entry.insert(0, role)
        role_entry.pack(pady=5)

        tk.Label(edit_window, text="Логин:").pack(pady=5)
        login_entry = tk.Entry(edit_window)
        login_entry.insert(0, login)
        login_entry.pack(pady=5)

        tk.Label(edit_window, text="Пароль:").pack(pady=5)
        password_entry = tk.Entry(edit_window)
        password_entry.insert(0, password)
        password_entry.pack(pady=5)

        def update_user():
            new_name = name_entry.get()
            new_role = role_entry.get()
            new_login = login_entry.get()
            new_password = password_entry.get()

            if not new_name or not new_role or not new_login or not new_password:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            # Получаем role_id по имени роли
            role_id = self.db.execute_query("SELECT role_id FROM Role WHERE name = %s", (new_role,))
            if not role_id:
                messagebox.showerror("Ошибка", "Роль не найдена")
                return

            self.db.execute_query(
                "UPDATE \"User\" SET name = %s, role_id = %s, login = %s, password = %s WHERE user_id = %s",
                (new_name, role_id[0][0], new_login, new_password, user_id), fetch=False)
            edit_window.destroy()
            self.load_users()

        tk.Button(edit_window, text="Сохранить", command=update_user).pack(pady=10)

    def delete_user(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите пользователя для удаления")
            return

        user_id = self.tree.item(selected_item)['values'][0]
        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить пользователя №{user_id}?")
        if confirm:
            self.db.execute_query("DELETE FROM \"User\" WHERE user_id = %s", (user_id,), fetch=False)
            self.load_users()