import sqlite3

class Database:
    def __init__(self, db_name="OctaDB.db"):
        self.conn = sqlite3.connect(db_name)

    def query(self, sql, params=None):
        cursor = self.conn.cursor()
        cursor.execute(sql, params or ())
        return cursor
