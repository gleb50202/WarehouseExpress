import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class ReportsWindow:
    def __init__(self, root):
        self.root = root
        self.db = Database()
        self.window = tk.Toplevel(self.root)
        self.window.title("Отчеты")
        self.window.geometry("800x600")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Отчеты", font=("Arial", 18)).pack(pady=20)

        self.report_type = tk.StringVar(value="customer_orders")
        tk.Radiobutton(self.window, text="Заказы клиентов", variable=self.report_type, value="customer_orders").pack(pady=5)
        tk.Radiobutton(self.window, text="Категории продуктов", variable=self.report_type, value="product_categories").pack(pady=5)
        tk.Radiobutton(self.window, text="Поставщики", variable=self.report_type, value="suppliers").pack(pady=5)
        tk.Radiobutton(self.window, text="Продажи продуктов", variable=self.report_type, value="product_sales").pack(pady=5)

        tk.Button(self.window, text="Сформировать отчет", command=self.generate_report).pack(pady=20)

    def generate_report(self):
        report_type = self.report_type.get()
        if report_type == "customer_orders":
            self.generate_customer_orders_report()
        elif report_type == "product_categories":
            self.generate_product_categories_report()
        elif report_type == "suppliers":
            self.generate_suppliers_report()
        elif report_type == "product_sales":
            self.generate_product_sales_report()

    def generate_customer_orders_report(self):
        report_window = tk.Toplevel(self.window)
        report_window.title("Отчет по заказам клиентов")
        report_window.geometry("800x600")

        tree = ttk.Treeview(report_window, columns=(
            "customer_login", "customer_role", "customer_name", "total_orders", "total_spent", "average_order_value", "last_order_date"), show="headings")

        tree.heading("customer_login", text="Логин клиента")
        tree.heading("customer_role", text="Роль клиента")
        tree.heading("customer_name", text="Имя клиента")
        tree.heading("total_orders", text="Всего заказов")
        tree.heading("total_spent", text="Всего потрачено")
        tree.heading("average_order_value", text="Средняя стоимость заказа")
        tree.heading("last_order_date", text="Дата последнего заказа")

        tree.column("customer_login", width=100)
        tree.column("customer_role", width=100)
        tree.column("customer_name", width=150)
        tree.column("total_orders", width=100)
        tree.column("total_spent", width=100)
        tree.column("average_order_value", width=150)
        tree.column("last_order_date", width=150)

        tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        query = """
        SELECT 
            u.login AS "CustomerLogin",
            r.name AS "CustomerRole",
            u.name AS "CustomerName",
            COUNT(o.order_id) AS "TotalOrders",
            SUM(oi.total_price) AS "TotalSpent",
            AVG(oi.total_price) AS "AverageOrderValue",
            MAX(o.order_date) AS "LastOrderDate"
        FROM "User" u
        JOIN Role r ON u.role_id = r.role_id
        JOIN "Order" o ON u.user_id = o.user_id
        JOIN Order_Item oi ON o.order_id = oi.order_id
        GROUP BY u.login, r.name, u.name;
        """

        orders = self.db.execute_query(query)
        for order in orders:
            tree.insert("", "end", values=order)

    def generate_product_categories_report(self):
        report_window = tk.Toplevel(self.window)
        report_window.title("Отчет по категориям продуктов")
        report_window.geometry("800x600")

        tree = ttk.Treeview(report_window, columns=(
            "category_name", "number_of_products", "average_price", "total_quantity_sold", "total_revenue"), show="headings")

        tree.heading("category_name", text="Название категории")
        tree.heading("number_of_products", text="Количество продуктов")
        tree.heading("average_price", text="Средняя цена")
        tree.heading("total_quantity_sold", text="Всего продано")
        tree.heading("total_revenue", text="Общий доход")

        tree.column("category_name", width=150)
        tree.column("number_of_products", width=150)
        tree.column("average_price", width=100)
        tree.column("total_quantity_sold", width=100)
        tree.column("total_revenue", width=100)

        tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        query = """
        SELECT 
            c.name AS "CategoryName",
            COUNT(p.product_id) AS "NumberOfProducts",
            AVG(p.price) AS "AveragePrice",
            SUM(oi.quantity) AS "TotalQuantitySold",
            SUM(oi.total_price) AS "TotalRevenue"
        FROM Category c
        LEFT JOIN Product p ON c.category_id = p.category_id
        LEFT JOIN Order_Item oi ON p.product_id = oi.product_id
        GROUP BY c.name;
        """

        categories = self.db.execute_query(query)
        for category in categories:
            tree.insert("", "end", values=category)

    def generate_suppliers_report(self):
        report_window = tk.Toplevel(self.window)
        report_window.title("Отчет по поставщикам")
        report_window.geometry("800x600")

        tree = ttk.Treeview(report_window, columns=(
            "supplier_name", "supplier_contact_info", "number_of_products", "total_quantity_supplied", "average_profit_margin"), show="headings")

        tree.heading("supplier_name", text="Название поставщика")
        tree.heading("supplier_contact_info", text="Контактная информация")
        tree.heading("number_of_products", text="Количество продуктов")
        tree.heading("total_quantity_supplied", text="Всего поставлено")
        tree.heading("average_profit_margin", text="Средняя маржа прибыли")

        tree.column("supplier_name", width=150)
        tree.column("supplier_contact_info", width=200)
        tree.column("number_of_products", width=150)
        tree.column("total_quantity_supplied", width=100)
        tree.column("average_profit_margin", width=150)

        tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        query = """
        SELECT 
            s.name AS "SupplierName",
            s.contact_info AS "SupplierContactInfo",
            COUNT(DISTINCT p.product_id) AS "NumberOfProducts",
            SUM(r.quantity) AS "TotalQuantitySupplied",
            AVG(p.price - s.purchase_price) AS "AverageProfitMargin"
        FROM Supplier s
        LEFT JOIN Product p ON s.supplier_id = p.supplier_id
        LEFT JOIN Receipt r ON s.supplier_id = r.supplier_id
        GROUP BY s.name, s.contact_info;
        """

        suppliers = self.db.execute_query(query)
        for supplier in suppliers:
            tree.insert("", "end", values=supplier)

    def generate_product_sales_report(self):
        report_window = tk.Toplevel(self.window)
        report_window.title("Отчет по продажам продуктов")
        report_window.geometry("800x600")

        tree = ttk.Treeview(report_window, columns=(
            "product_name", "article_number", "category_name", "total_quantity_sold", "total_revenue", "number_of_orders"), show="headings")

        tree.heading("product_name", text="Название продукта")
        tree.heading("article_number", text="Артикул")
        tree.heading("category_name", text="Категория")
        tree.heading("total_quantity_sold", text="Всего продано")
        tree.heading("total_revenue", text="Общий доход")
        tree.heading("number_of_orders", text="Количество заказов")

        tree.column("product_name", width=150)
        tree.column("article_number", width=100)
        tree.column("category_name", width=150)
        tree.column("total_quantity_sold", width=100)
        tree.column("total_revenue", width=100)
        tree.column("number_of_orders", width=100)

        tree.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(report_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        query = """
        SELECT 
            p.name AS "ProductName",
            p.article_number AS "ArticleNumber",
            c.name AS "CategoryName",
            SUM(oi.quantity) AS "TotalQuantitySold",
            SUM(oi.total_price) AS "TotalRevenue",
            COUNT(DISTINCT o.order_id) AS "NumberOfOrders"
        FROM Product p
        JOIN Order_Item oi ON p.product_id = oi.product_id
        JOIN "Order" o ON oi.order_id = o.order_id
        JOIN Category c ON p.category_id = c.category_id
        GROUP BY p.name, p.article_number, c.name;
        """

        products = self.db.execute_query(query)
        for product in products:
            tree.insert("", "end", values=product)