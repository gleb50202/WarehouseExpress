import psycopg2

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            database="WarehouseExpress",
            user="postgres",
            password="1525",
            host="127.0.0.1",
            port="5432"
        )

    def execute_query(self, query, params=None, fetch=True):
        self.cursor = self.conn.cursor()
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)

        if fetch:
            result = self.cursor.fetchall()
        else:
            result = None

        self.conn.commit()
        self.cursor.close()
        return result

    def close(self):
        self.cursor.close()
        self.conn.close()