import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from datetime import datetime

class OrdersWindow:
    def __init__(self, root, user_info):
        self.root = root
        self.db = Database()
        self.window = tk.Toplevel(self.root)
        self.window.title("Заказы")
        self.window.geometry("800x600")
        self.user_info = user_info
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Заказы", font=("Arial", 18)).pack(pady=20)

        # Создаем таблицу для отображения заказов
        self.tree = ttk.Treeview(self.window, columns=(
            "order_id", "full_name", "order_date", "order_status", "delivery_address", "customer_contact_info"), show="headings")

        # Определяем заголовки столбцов
        self.tree.heading("order_id", text="Номер заказа")
        self.tree.heading("full_name", text="Пользователь")
        self.tree.heading("order_date", text="Дата заказа")
        self.tree.heading("order_status", text="Статус")
        self.tree.heading("delivery_address", text="Адрес")
        self.tree.heading("customer_contact_info", text="Контактная информация")

        # Устанавливаем ширину столбцов
        self.tree.column("order_id", width=100)
        self.tree.column("full_name", width=150)
        self.tree.column("order_date", width=150)
        self.tree.column("delivery_address", width=150)
        self.tree.column("order_status", width=150)
        self.tree.column("customer_contact_info", width=150)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_orders()

        tk.Button(self.window, text="Добавить заказ", command=self.add_order).pack(pady=10)
        tk.Button(self.window, text="Редактировать заказ", command=self.edit_order).pack(pady=10)
        tk.Button(self.window, text="Удалить заказ", command=self.delete_order).pack(pady=10)

    def load_orders(self):
        # Очищаем таблицу
        for i in self.tree.get_children():
            self.tree.delete(i)

        query = """
                SELECT
                o.order_id AS "Order ID",
                u.name AS "Customer Name",
                o.order_date AS "Order Date",
                o.order_status AS "Order Status",
                o.delivery_address AS "Delivery Address",
                o.customer_contact_info AS "Contact Info"
                FROM "Order" o
                JOIN "User" u ON o.user_id = u.user_id
                ORDER BY o.order_id;
        """

        # Загружаем заказы из базы данных
        orders = self.db.execute_query(query)
        for order in orders:
            self.tree.insert("", "end", values=order)

    def add_order(self):
        # Создаем диалоговое окно для добавления заказа
        add_window = tk.Toplevel(self.window)
        add_window.title("Добавить заказ")
        add_window.geometry("400x300")

        tk.Label(add_window, text="Дата заказа:").pack(pady=5)
        order_date_entry = tk.Entry(add_window)
        order_date_entry.pack(pady=5)

        tk.Label(add_window, text="Адрес:").pack(pady=5)
        delivery_address_entry = tk.Entry(add_window)
        delivery_address_entry.pack(pady=5)

        tk.Label(add_window, text="Статус:").pack(pady=5)
        order_status_entry = tk.Entry(add_window)
        order_status_entry.pack(pady=5)

        tk.Label(add_window, text="Контактная информация:").pack(pady=5)
        customer_contact_info_entry = tk.Entry(add_window)
        customer_contact_info_entry.pack(pady=5)

        def save_order():
            order_date = order_date_entry.get()
            delivery_address = delivery_address_entry.get()
            order_status = order_status_entry.get()
            customer_contact_info = customer_contact_info_entry.get()

            if not order_date or not delivery_address or not order_status or not customer_contact_info:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            # Убедитесь, что даты передаются в правильном формате
            try:
                order_date = datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте формат YYYY-MM-DD HH:MM:SS")
                return

            query = """
            INSERT INTO "Order" (order_date, order_status, delivery_address, customer_contact_info, user_id) VALUES (%s, %s, %s, %s, %s)
            """

            self.db.execute_query(
                query,
                (order_date, order_status, delivery_address, customer_contact_info, self.user_info[0]), fetch=False)
            add_window.destroy()
            self.load_orders()

        tk.Button(add_window, text="Сохранить", command=save_order).pack(pady=10)

    def edit_order(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите заказ для редактирования")
            return

        order_id = self.tree.item(selected_item)['values'][0]
        order_date = self.tree.item(selected_item)['values'][2]
        delivery_address = self.tree.item(selected_item)['values'][3]
        order_status = self.tree.item(selected_item)['values'][4]
        customer_contact_info = self.tree.item(selected_item)['values'][5]

        # Создаем диалоговое окно для редактирования заказа
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Редактировать заказ")
        edit_window.geometry("400x300")

        tk.Label(edit_window, text="Дата заказа:").pack(pady=5)
        order_date_entry = tk.Entry(edit_window)
        order_date_entry.insert(0, order_date)
        order_date_entry.pack(pady=5)

        tk.Label(edit_window, text="Адрес:").pack(pady=5)
        delivery_address_entry = tk.Entry(edit_window)
        delivery_address_entry.insert(0, delivery_address)
        delivery_address_entry.pack(pady=5)

        tk.Label(edit_window, text="Статус:").pack(pady=5)
        order_status_entry = tk.Entry(edit_window)
        order_status_entry.insert(0, order_status)
        order_status_entry.pack(pady=5)

        tk.Label(edit_window, text="Контактная информация:").pack(pady=5)
        customer_contact_info_entry = tk.Entry(edit_window)
        customer_contact_info_entry.insert(0, customer_contact_info)
        customer_contact_info_entry.pack(pady=5)

        def update_order():
            new_order_date = order_date_entry.get()
            new_delivery_address = delivery_address_entry.get()
            new_order_status = order_status_entry.get()
            new_customer_contact_info = customer_contact_info_entry.get()

            if not new_order_date or not new_delivery_address or not new_order_status or not new_customer_contact_info:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            # Убедитесь, что даты передаются в правильном формате
            try:
                new_order_date = datetime.strptime(new_order_date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте формат YYYY-MM-DD HH:MM:SS")
                return

            query = """
            UPDATE "Order" SET order_date = %s, delivery_address = %s, order_status = %s, customer_contact_info = %s WHERE order_id = %s
            """

            self.db.execute_query(
                query,
                (new_order_date, new_delivery_address, new_order_status, new_customer_contact_info, order_id), fetch=False)
            edit_window.destroy()
            self.load_orders()

        tk.Button(edit_window, text="Сохранить", command=update_order).pack(pady=10)

    def delete_order(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите заказ для удаления")
            return

        order_id = self.tree.item(selected_item)['values'][0]
        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить заказ №{order_id}?")
        if confirm:
            query = """
            DELETE FROM "Order" WHERE order_id = %s
            """
            self.db.execute_query(query, (order_id,), fetch=False)
            self.load_orders()