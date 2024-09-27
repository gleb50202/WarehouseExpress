import unittest
from unittest.mock import MagicMock, patch
from tkinter import Tk, Button, Entry, END
from ui.main_window import MainWindow


class TestMainWindow(unittest.TestCase):

    def setUp(self):
        self.root = Tk()
        self.user_info = [
            (1, "Администратор", "John Doe", "john_doe", "password")
        ]
        self.main_window = MainWindow(self.root, self.user_info)
        self.main_window.__init__(self.root, self.user_info)

    def tearDown(self):
        self.root.destroy()

    def test_create_widgets_for_admin(self):
        # Проверяем, что для администратора создаются все кнопки
        buttons = [child for child in self.main_window.root.winfo_children()[0].winfo_children() if
                   isinstance(child, Button)]
        self.assertEqual(len(buttons), 4)
        button_texts = [button.cget('text') for button in buttons]
        self.assertIn("Заказы", button_texts)
        self.assertIn("Товары", button_texts)
        self.assertIn("Отчеты", button_texts)
        self.assertIn("Администрирование", button_texts)

    @patch('ui.main_window.OrdersWindow')
    @patch('ui.main_window.MainWindow.create_widgets')
    def test_open_orders(self, mock_create_widgets, mock_orders_window):
        # Создание экземпляра MainWindow
        main_window = MainWindow(MagicMock(), self.user_info)

        # Вызов метода open_orders
        main_window.open_orders()

        # Проверка, что OrdersWindow был вызван с правильными аргументами
        mock_orders_window.assert_called_once_with(main_window.root, main_window.user_info)

    @patch('database.Database.execute_query')
    @patch('tkinter.messagebox.showerror')
    @patch('tkinter.Toplevel')
    @patch('ui.main_window.MainWindow.create_widgets')
    def test_track_order_success(self, mock_create_widgets, mock_toplevel, mock_showerror, mock_execute_query):
        # Подготовка данных для теста
        mock_execute_query.return_value = [
            ("1", "2023-09-27", "В обработке", "Адрес доставки", "Контакт", "John Doe", "Товар 1", "ART001", "2", "100.00")
        ]

        # Создание экземпляра MainWindow
        main_window = MainWindow(MagicMock(), self.user_info)

        # Мокирование ввода данных
        main_window.order_entry = MagicMock()
        main_window.order_entry.get.return_value = '1'

        # Вызов метода track_order
        main_window.track_order()

        # Проверка, что execute_query был вызван с правильными аргументами
        expected_query_parts = [
            'o.order_id AS "Номер заказа"',
            'o.order_date AS "Дата заказа"',
            'o.order_status AS "Статус заказа"',
            'o.delivery_address AS "Адрес"',
            'o.customer_contact_info AS "Контактная информация"',
            'u.name AS "Имя"',
            'p.name AS "Наименование продукта"',
            'p.article_number AS "Артикул"',
            'oi.quantity AS "Количество"',
            'oi.total_price AS "Итоговая стоимость"',
            'FROM "Order" o',
            'JOIN "User" u ON o.user_id = u.user_id',
            'JOIN Order_Item oi ON o.order_id = oi.order_id',
            'JOIN Product p ON oi.product_id = p.product_id',
            'WHERE o.order_id = %s'
        ]
        actual_query = mock_execute_query.call_args[0][0]
        for part in expected_query_parts:
            self.assertIn(part, actual_query)

        # Проверка, что showerror не был вызван
        mock_showerror.assert_not_called()

        # Проверка, что Toplevel был вызван
        mock_toplevel.assert_called_once()

    @patch('database.Database.execute_query')
    @patch('tkinter.messagebox.showerror')
    @patch('ui.main_window.MainWindow.create_widgets')
    def test_track_order_not_found(self, mock_create_widgets, mock_showerror, mock_execute_query):
        # Подготовка данных для теста
        mock_execute_query.return_value = []

        # Создание экземпляра MainWindow
        main_window = MainWindow(MagicMock(), self.user_info)

        # Мокирование ввода данных
        main_window.order_entry = MagicMock()
        main_window.order_entry.get.return_value = '1'

        # Вызов метода track_order
        main_window.track_order()

        # Проверка, что execute_query был вызван с правильными аргументами
        expected_query_parts = [
            'o.order_id AS "Номер заказа"',
            'o.order_date AS "Дата заказа"',
            'o.order_status AS "Статус заказа"',
            'o.delivery_address AS "Адрес"',
            'o.customer_contact_info AS "Контактная информация"',
            'u.name AS "Имя"',
            'p.name AS "Наименование продукта"',
            'p.article_number AS "Артикул"',
            'oi.quantity AS "Количество"',
            'oi.total_price AS "Итоговая стоимость"',
            'FROM "Order" o',
            'JOIN "User" u ON o.user_id = u.user_id',
            'JOIN Order_Item oi ON o.order_id = oi.order_id',
            'JOIN Product p ON oi.product_id = p.product_id',
            'WHERE o.order_id = %s'
        ]
        actual_query = mock_execute_query.call_args[0][0]
        for part in expected_query_parts:
            self.assertIn(part, actual_query)

        # Проверка, что showerror был вызван с правильными аргументами
        mock_showerror.assert_called_once_with("Ошибка", "Заказ не найден")

import unittest
from unittest.mock import MagicMock, patch
from tkinter import Tk, ttk
from ui.orders_window import OrdersWindow


class TestOrdersWindow(unittest.TestCase):

    def setUp(self):
        self.root = Tk()
        self.user_info = [(1, "Администратор", "John Doe", "john_doe", "password")]
        self.orders_window = OrdersWindow(self.root, self.user_info)

    def tearDown(self):
        self.root.destroy()

    def test_create_widgets(self):
        # Проверяем, что виджеты создаются корректно
        self.assertIsInstance(self.orders_window.tree, ttk.Treeview)
        self.assertEqual(self.orders_window.tree.heading("order_id")['text'], "Номер заказа")
        self.assertEqual(self.orders_window.tree.heading("full_name")['text'], "Пользователь")
        self.assertEqual(self.orders_window.tree.heading("order_date")['text'], "Дата заказа")
        self.assertEqual(self.orders_window.tree.heading("order_status")['text'], "Статус")
        self.assertEqual(self.orders_window.tree.heading("delivery_address")['text'], "Адрес")
        self.assertEqual(self.orders_window.tree.heading("customer_contact_info")['text'], "Контактная информация")

    @patch('ui.orders_window.Database')
    @patch('tkinter.messagebox.showerror')
    def test_add_order_success(self, mock_showerror, mock_db):
        # Подготавливаем мок-данные для добавления заказа
        mock_db.return_value.execute_query.return_value = None

        # Мокируем ввод данных
        self.orders_window.order_date_entry = MagicMock()
        self.orders_window.order_date_entry.get.return_value = "2023-09-27 12:00:00"
        self.orders_window.delivery_address_entry = MagicMock()
        self.orders_window.delivery_address_entry.get.return_value = "Address 1"
        self.orders_window.order_status_entry = MagicMock()
        self.orders_window.order_status_entry.get.return_value = "Pending"
        self.orders_window.customer_contact_info_entry = MagicMock()
        self.orders_window.customer_contact_info_entry.get.return_value = "Contact Info 1"
        self.orders_window.user_id_entry = MagicMock()
        self.orders_window.user_id_entry.get.return_value = 1


        # Вызываем метод add_order
        self.orders_window.add_order()

        # Проверяем, что заказ был добавлен в базу данных
        expected_query = """
            INSERT INTO "Order" (order_date, order_status, delivery_address, customer_contact_info, user_id) VALUES (%s, %s, %s, %s, %s)
        """
        self.assertIn(expected_query, mock_db.return_value.execute_query.call_args[0][0])
        self.assertEqual(mock_db.return_value.execute_query.call_args[0][1],
                         ("2023-09-27 12:00:00", "Pending", "Address 1", "Contact Info 1", 1))

        # Проверяем, что сообщение об ошибке не было показано
        mock_showerror.assert_not_called()

    @patch('ui.orders_window.Database')
    @patch('tkinter.messagebox.showerror')
    def test_edit_order_success(self, mock_showerror, mock_db):
        # Подготавливаем мок-данные для редактирования заказа
        mock_db.return_value.execute_query.return_value = None

        # Мокируем выбор заказа
        self.orders_window.tree.insert("", "end", values=(1, "John Doe", "2023-09-27 12:00:00", "В обработке", "Адрес 1", "Контакт 1"))
        self.orders_window.tree.selection_set(self.orders_window.tree.get_children()[0])

        # Мокируем ввод данных
        self.orders_window.order_date_entry = MagicMock()
        self.orders_window.order_date_entry.get.return_value = "2023-09-28 12:00:00"
        self.orders_window.delivery_address_entry = MagicMock()
        self.orders_window.delivery_address_entry.get.return_value = "Адрес 2"
        self.orders_window.order_status_entry = MagicMock()
        self.orders_window.order_status_entry.get.return_value = "Доставлен"
        self.orders_window.customer_contact_info_entry = MagicMock()
        self.orders_window.customer_contact_info_entry.get.return_value = "Контакт 2"

        # Вызываем метод edit_order
        self.orders_window.edit_order()

        # Проверяем, что заказ был обновлен в базе данных
        expected_query = """
            UPDATE "Order" SET order_date = %s, delivery_address = %s, order_status = %s, customer_contact_info = %s WHERE order_id = %s
        """
        self.assertIn(expected_query, mock_db.return_value.execute_query.call_args[0][0])
        self.assertEqual(mock_db.return_value.execute_query.call_args[0][1],
                         ("2023-09-28 12:00:00", "Адрес 2", "Доставлен", "Контакт 2", 1))

        # Проверяем, что сообщение об ошибке не было показано
        mock_showerror.assert_not_called()

    @patch('ui.orders_window.Database')
    @patch('tkinter.messagebox.askyesno')
    def test_delete_order_success(self, mock_askyesno, mock_db):
        # Подготавливаем мок-данные для удаления заказа
        mock_db.return_value.execute_query.return_value = None
        mock_askyesno.return_value = True

        # Мокируем выбор заказа
        self.orders_window.tree.insert("", "end", values=(1, "John Doe", "2023-09-27 12:00:00", "В обработке", "Адрес 1", "Контакт 1"))
        self.orders_window.tree.selection_set(self.orders_window.tree.get_children()[0])

        # Вызываем метод delete_order
        self.orders_window.delete_order()

        # Проверяем, что заказ был удален из базы данных
        expected_query = """
            DELETE FROM "Order" WHERE order_id = %s
        """
        self.assertIn(expected_query, mock_db.return_value.execute_query.call_args[0][0])
        self.assertEqual(mock_db.return_value.execute_query.call_args[0][1], (1,))

        # Проверяем, что подтверждение было запрошено
        mock_askyesno.assert_called_once_with("Подтверждение", "Вы уверены, что хотите удалить заказ №1?")

if __name__ == '__main__':
    unittest.main()