import sqlite3
import os
class DbHandle(object):
    def __init__(self):
        dbPath=os.path.join(os.getcwd(),os.path.join('data',"result.db"))
        self.conn = sqlite3.connect(dbPath)
        self.cursor = self.conn.cursor()
    def createTables(self):
        sql="drop table if exists lp"
        self.cursor.execute(sql)
        sql="""
            create table if not exists lp(
                id integer primary key AUTOINCREMENT,
                product varchar(20),
                test_date date,
                temperature integer,
                bh varchar(20),
                lp real,
                lp_wdx real,
                data_file varchar(100)
            )
        """
        self.cursor.execute(sql)
        sql="drop table if exists lp_cfx"
        self.cursor.execute(sql)
        sql="""
            create table if not exists lp_cfx(
                id integer primary key AUTOINCREMENT,
                product varchar(20),
                test_date date,
                temperature integer,
                bh varchar(20),
                lp_cfx real,
                data_file varchar(100)
            )
        """
        self.cursor.execute(sql)
        sql="drop table if exists bdys"
        self.cursor.execute(sql)
        sql="""
            create table if not exists bdys(
                id integer primary key AUTOINCREMENT,
                product varchar(20),
                test_date date,
                temperature integer,
                bh varchar(20),
                bdys real,
                bdys_xxd real,
                data_file varchar(100)
            )
        """
        self.cursor.execute(sql)
        sql="drop table if exists bdys_cfx"
        self.cursor.execute(sql)
        sql="""
            create table if not exists bdys_cfx(
                id integer primary key AUTOINCREMENT,
                product varchar(20),
                test_date date,
                temperature integer,
                bh varchar(20),
                bdys real,
                bdys_xxd real,
                data_file varchar(100)
            )
        """
        self.cursor.execute(sql)
    def insert_lp(self,product,date,temperature,bh,lp,lp_wdx,data_file):
        sql="""
        insert into lp (product,test_date,temperature,bh,lp,lp_wdx,data_file) values (\'%s\',\'%s\',%d,\'%s\',%f,%f,\'%s\')
        """ %(product,date,temperature,bh,lp,lp_wdx,data_file)
        print (sql)
        self.cursor.execute(sql)
    def insert_lp_cfx(self,product,date,temperature,bh,lp_cfx,data_file):
        sql="""
        insert into lp_cfx (product,test_date,temperature,bh,lp_cfx,data_file) values (\'%s\',\'%s\',%d,\'%s\',%f,\'%s\')
        """ %(product,date,temperature,bh,lp_cfx,data_file)
        print (sql)
        self.cursor.execute(sql)
    def insert_bdys(self,product,date,temperature,bh,bdys,bdys_xxd,data_file):
        sql="""
        insert into bdys (product,test_date,temperature,bh,bdys,bdys_xxd,data_file) values (\'%s\',\'%s\',%d,\'%s\',%f,%f,\'%s\')
        """ %(product,date,temperature,bh,bdys,bdys_xxd,data_file)
        print (sql)
        self.cursor.execute(sql)  
    def insert_bdys_cfx(self,product,date,temperature,bh,bdys,bdys_xxd,data_file):
        sql="""
        insert into bdys_cfx (product,test_date,temperature,bh,bdys,bdys_xxd,data_file) values (\'%s\',\'%s\',%d,\'%s\',%f,%f,\'%s\')
        """ %(product,date,temperature,bh,bdys,bdys_xxd,data_file)
        print (sql)
        self.cursor.execute(sql)  
    def search(self,sql):
        self.cursor.execute(sql)
        values=self.cursor.fetchall()
        return values

    def __del__(self):
        self.cursor.close()
        self.conn.close()
"""
db=DbHandle()
db.createTables()
del db

db=DbHandle()
sql='select * from lp'
print(db.search(sql))
"""