import sqlite3


class DBManager:

    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.curs = self.conn.cursor()

    def get_all(self):
        q = """select * from exp_dates"""
        self.curs.execute(q)
        return self.curs.fetchall()

    def get_exp_time(self, filename):
        q = """select exp_date from exp_dates where filename=?"""
        self.curs.execute(q, (filename,))
        return self.curs.fetchone()[0]

    def search_on_filename(self, filename):
        q = """select * from exp_dates where filename=?"""
        self.curs.execute(q, (filename,))
        return bool(self.curs.fetchall())

    def is_file_exists(self, filename):
        return self.search_on_filename(filename)

    def insert_data(self, filename, exp_date):
        q = """insert into exp_dates values (?, ?)"""
        self.curs.execute(q, (filename, exp_date))
        self.conn.commit()

    def remove_file(self, filename):
        q = """delete from exp_dates where filename=?"""
        self.curs.execute(q, (filename,))
        self.conn.commit()

    def connect(self):
        self.conn = sqlite3.connect(self.path)
        self.curs = self.conn.cursor()

    def disconnect(self):
        self.conn.close()
