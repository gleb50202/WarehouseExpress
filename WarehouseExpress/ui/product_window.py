import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class ProductWindow:
    def __init__(self, root, user_info):
        self.root = root
        self.db = Database()
        self.window = tk.Toplevel(self.root)
        self.window.title("Продукты")
        self.window.geometry("1200x800")  # Увеличиваем размер окна для двух таблиц
        self.user_info = user_info

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Продукты", font=("Arial", 18)).pack(pady=20)

        # Создаем таблицу для отображения продуктов
        self.tree = ttk.Treeview(self.window, columns=(
            "product_id", "product_name", "article_number", "category", "price", "supplier_name", "supplier_contact_info"), show="headings")

        # Определяем заголовки столбцов
        self.tree.heading("product_id", text="ID продукта")
        self.tree.heading("product_name", text="Название продукта")
        self.tree.heading("article_number", text="Артикул")
        self.tree.heading("category", text="Категория")
        self.tree.heading("price", text="Цена")
        self.tree.heading("supplier_name", text="Поставщик")
        self.tree.heading("supplier_contact_info", text="Контактная информация поставщика")

        # Устанавливаем ширину столбцов
        self.tree.column("product_id", width=100)
        self.tree.column("product_name", width=150)
        self.tree.column("article_number", width=100)
        self.tree.column("category", width=150)
        self.tree.column("price", width=100)
        self.tree.column("supplier_name", width=150)
        self.tree.column("supplier_contact_info", width=200)

        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.TOP, padx=10, pady=10)

        # Добавляем полосу прокрутки для первой таблицы
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_products()

        tk.Button(self.window, text="Добавить продукт", command=self.add_product).pack(pady=10)
        tk.Button(self.window, text="Редактировать продукт", command=self.edit_product).pack(pady=10)
        tk.Button(self.window, text="Удалить продукт", command=self.delete_product).pack(pady=10)

        # Создаем вторую таблицу для отображения статистики продуктов
        self.tree_stats = ttk.Treeview(self.window, columns=(
            "product_name", "article_number", "category_name", "supplier_name", "total_received", "total_sold", "current_stock", "current_price", "stock_value"), show="headings")

        # Определяем заголовки столбцов
        self.tree_stats.heading("product_name", text="Название продукта")
        self.tree_stats.heading("article_number", text="Артикул")
        self.tree_stats.heading("category_name", text="Категория")
        self.tree_stats.heading("supplier_name", text="Поставщик")
        self.tree_stats.heading("total_received", text="Всего получено")
        self.tree_stats.heading("total_sold", text="Всего продано")
        self.tree_stats.heading("current_stock", text="Текущий запас")
        self.tree_stats.heading("current_price", text="Текущая цена")
        self.tree_stats.heading("stock_value", text="Стоимость запаса")

        # Устанавливаем ширину столбцов
        self.tree_stats.column("product_name", width=150)
        self.tree_stats.column("article_number", width=100)
        self.tree_stats.column("category_name", width=150)
        self.tree_stats.column("supplier_name", width=150)
        self.tree_stats.column("total_received", width=100)
        self.tree_stats.column("total_sold", width=100)
        self.tree_stats.column("current_stock", width=100)
        self.tree_stats.column("current_price", width=100)
        self.tree_stats.column("stock_value", width=100)

        self.tree_stats.pack(fill=tk.BOTH, expand=True, side=tk.BOTTOM, padx=10, pady=10)

        # Добавляем полосу прокрутки для второй таблицы
        scrollbar_stats = ttk.Scrollbar(self.window, orient="vertical", command=self.tree_stats.yview)
        self.tree_stats.configure(yscrollcommand=scrollbar_stats.set)
        scrollbar_stats.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_product_stats()

    def load_products(self):
        # Очищаем таблицу
        for i in self.tree.get_children():
            self.tree.delete(i)

        query = """
        SELECT
            p.product_id AS "Product ID",
            p.name AS "Product Name",
            p.article_number AS "Article",
            c.name AS "Category",
            p.price AS "Price",
            s.name AS "Supplier Name",
            s.contact_info AS "Supplier Contact Info"
        FROM Product p
        JOIN Category c ON p.category_id = c.category_id
        JOIN Supplier s ON p.supplier_id = s.supplier_id
        ORDER BY p.product_id;
        """

        # Загружаем продукты из базы данных
        products = self.db.execute_query(query)
        for product in products:
            self.tree.insert("", "end", values=product)

    def load_product_stats(self):
        # Очищаем таблицу
        for i in self.tree_stats.get_children():
            self.tree_stats.delete(i)

        query = """
        SELECT
            p.name AS "ProductName",
            p.article_number AS "ArticleNumber",
            c.name AS "CategoryName",
            s.name AS "SupplierName",
            SUM(r.quantity) AS "TotalReceived",
            COALESCE(SUM(oi.quantity), 0) AS "TotalSold",
            SUM(r.quantity) - COALESCE(SUM(oi.quantity), 0) AS "CurrentStock",
            p.price AS "CurrentPrice",
            (SUM(r.quantity) - COALESCE(SUM(oi.quantity), 0)) * p.price AS "StockValue"
        FROM Product p
        JOIN Category c ON p.category_id = c.category_id
        JOIN Supplier s ON p.supplier_id = s.supplier_id
        LEFT JOIN Receipt r ON p.product_id = r.product_id
        LEFT JOIN Order_Item oi ON p.product_id = oi.product_id
        GROUP BY p.name, p.article_number, c.name, s.name, p.price;
        """

        # Загружаем статистику продуктов из базы данных
        product_stats = self.db.execute_query(query)
        for stat in product_stats:
            self.tree_stats.insert("", "end", values=stat)


    def add_product(self):
        # Создаем диалоговое окно для добавления продукта
        add_window = tk.Toplevel(self.window)
        add_window.title("Добавить продукт")
        add_window.geometry("400x300")

        tk.Label(add_window, text="Название продукта:").pack(pady=5)
        product_name_entry = tk.Entry(add_window)
        product_name_entry.pack(pady=5)

        tk.Label(add_window, text="Артикул:").pack(pady=5)
        article_number_entry = tk.Entry(add_window)
        article_number_entry.pack(pady=5)

        tk.Label(add_window, text="Категория:").pack(pady=5)
        category_entry = tk.Entry(add_window)
        category_entry.pack(pady=5)

        tk.Label(add_window, text="Цена:").pack(pady=5)
        price_entry = tk.Entry(add_window)
        price_entry.pack(pady=5)

        tk.Label(add_window, text="Поставщик:").pack(pady=5)
        supplier_name_entry = tk.Entry(add_window)
        supplier_name_entry.pack(pady=5)

        tk.Label(add_window, text="Контактная информация поставщика:").pack(pady=5)
        supplier_contact_info_entry = tk.Entry(add_window)
        supplier_contact_info_entry.pack(pady=5)

        def save_product():
            product_name = product_name_entry.get()
            article_number = article_number_entry.get()
            category = category_entry.get()
            price = price_entry.get()
            supplier_name = supplier_name_entry.get()
            supplier_contact_info = supplier_contact_info_entry.get()

            if not product_name or not article_number or not category or not price or not supplier_name or not supplier_contact_info:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            # Получаем category_id и supplier_id по имени категории и поставщика
            category_id = self.db.execute_query("SELECT category_id FROM Category WHERE name = %s", (category,))
            if not category_id:
                messagebox.showerror("Ошибка", "Категория не найдена")
                return

            supplier_id = self.db.execute_query("SELECT supplier_id FROM Supplier WHERE name = %s", (supplier_name,))
            if not supplier_id:
                messagebox.showerror("Ошибка", "Поставщик не найден")
                return

            self.db.execute_query(
                "INSERT INTO Product (name, article_number, category_id, price, supplier_id) VALUES (%s, %s, %s, %s, %s)",
                (product_name, article_number, category_id[0][0], price, supplier_id[0][0]), fetch=False)
            add_window.destroy()
            self.load_products()

        tk.Button(add_window, text="Сохранить", command=save_product).pack(pady=10)

    def edit_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите продукт для редактирования")
            return

        product_id = self.tree.item(selected_item)['values'][0]
        product_name = self.tree.item(selected_item)['values'][1]
        article_number = self.tree.item(selected_item)['values'][2]
        category = self.tree.item(selected_item)['values'][3]
        price = self.tree.item(selected_item)['values'][4]
        supplier_name = self.tree.item(selected_item)['values'][5]
        supplier_contact_info = self.tree.item(selected_item)['values'][6]

        # Создаем диалоговое окно для редактирования продукта
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Редактировать продукт")
        edit_window.geometry("400x300")

        tk.Label(edit_window, text="Название продукта:").pack(pady=5)
        product_name_entry = tk.Entry(edit_window)
        product_name_entry.insert(0, product_name)
        product_name_entry.pack(pady=5)

        tk.Label(edit_window, text="Артикул:").pack(pady=5)
        article_number_entry = tk.Entry(edit_window)
        article_number_entry.insert(0, article_number)
        article_number_entry.pack(pady=5)

        tk.Label(edit_window, text="Категория:").pack(pady=5)
        category_entry = tk.Entry(edit_window)
        category_entry.insert(0, category)
        category_entry.pack(pady=5)

        tk.Label(edit_window, text="Цена:").pack(pady=5)
        price_entry = tk.Entry(edit_window)
        price_entry.insert(0, price)
        price_entry.pack(pady=5)

        tk.Label(edit_window, text="Поставщик:").pack(pady=5)
        supplier_name_entry = tk.Entry(edit_window)
        supplier_name_entry.insert(0, supplier_name)
        supplier_name_entry.pack(pady=5)

        tk.Label(edit_window, text="Контактная информация поставщика:").pack(pady=5)
        supplier_contact_info_entry = tk.Entry(edit_window)
        supplier_contact_info_entry.insert(0, supplier_contact_info)
        supplier_contact_info_entry.pack(pady=5)

        def update_product():
            new_product_name = product_name_entry.get()
            new_article_number = article_number_entry.get()
            new_category = category_entry.get()
            new_price = price_entry.get()
            new_supplier_name = supplier_name_entry.get()
            new_supplier_contact_info = supplier_contact_info_entry.get()

            if not new_product_name or not new_article_number or not new_category or not new_price or not new_supplier_name or not new_supplier_contact_info:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            # Получаем category_id и supplier_id по имени категории и поставщика
            category_id = self.db.execute_query("SELECT category_id FROM Category WHERE name = %s", (new_category,))
            if not category_id:
                messagebox.showerror("Ошибка", "Категория не найдена")
                return

            supplier_id = self.db.execute_query("SELECT supplier_id FROM Supplier WHERE name = %s", (new_supplier_name,))
            if not supplier_id:
                messagebox.showerror("Ошибка", "Поставщик не найден")
                return

            self.db.execute_query(
                "UPDATE Product SET name = %s, article_number = %s, category_id = %s, price = %s, supplier_id = %s WHERE product_id = %s",
                (new_product_name, new_article_number, category_id[0][0], new_price, supplier_id[0][0], product_id), fetch=False)
            edit_window.destroy()
            self.load_products()

        tk.Button(edit_window, text="Сохранить", command=update_product).pack(pady=10)

    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите продукт для удаления")
            return

        product_id = self.tree.item(selected_item)['values'][0]
        confirm = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить продукт №{product_id}?")
        if confirm:
            self.db.execute_query("DELETE FROM Product WHERE product_id = %s", (product_id,), fetch=False)
            self.load_products()