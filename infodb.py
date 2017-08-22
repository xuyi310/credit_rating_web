# -*- coding: UTF-8 -*-
import sys
import sqlite3
import xlrd

reload(sys)
sys.setdefaultencoding('utf-8')

def create_table():
    #pro_arr = []
    #for line in open('pro.list'):
    #    info = line.strip().split(' ')
    #    pro_arr.append([info[1], info[2]])
        
    exec_str = "CREATE TABLE main_info ("
    exec_str += "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    for item in pro_arr:
        exec_str += item[0] + " " + item[1] + ","
    exec_str = exec_str[:-1] + " )"
    
    print exec_str
    conn.execute(exec_str)

    exec_str = "CREATE TABLE log_info ("
    exec_str += "id INTEGER PRIMARY KEY AUTOINCREMENT,"
    for item in pro_arr:
        exec_str += item[0] + "_new " + item[1] + ","
        exec_str += item[0] + "_old " + item[1] + ","
    exec_str += "insert_time CHAR(100), author CHAR(100), type CHAR(100)"
    exec_str = exec_str + " )"
    print exec_str
    conn.execute(exec_str)


def insert_table( value=[]):
    exec_str = "INSERT INTO main_info (id, " 
    pro_str = ''
    
    for item in pro_arr:
        pro_str += item[0] + ", "
    pro_str = pro_str[:-2]
    exec_str += pro_str + ") VALUES ("
    
    val_str =  'NULL, '
    for item in value:
        val_str += '"' + item + '", '
    val_str = val_str[:-2]
    exec_str += val_str + ");"

    print exec_str
    conn.execute(exec_str)
    #conn.execute('INSERT INTO main_info (id, name, date, mainIndex, abbre, itemIndex) VALUES (1, "a", "b", "c", "d", "e");')
    conn.commit()
   
def show_table():
    cursor = conn.execute("SELECT * FROM main_info")
    for row in cursor:
        print row

    cursor = conn.execute("SELECT * FROM log_info")
    for row in cursor:
        print row

def delete_table(id=""):
    conn.execute("DELETE FROM main_info WHERE id='"+id+"'")
    conn.commit()

def clean_table():
    conn.execute("DELETE FROM main_info")
    conn.execute("DELETE FROM log_info")
    conn.commit()

def excel_insert(file_name='uploads/test-1.xlsx'):
    work_book = xlrd.open_workbook(file_name)
    sh = work_book.sheet_by_index(0)
    for idx_row in range(sh.nrows):
        exec_str = "INSERT INTO main_info VALUES ("
        val_str = 'NULL, '
        for i in range(0, len(sh.row(idx_row))):
            item_value = sh.row(idx_row)[i].value
            item_value = str(item_value).encode('utf8')
            val_str += '"' + item_value + '", '
        val_str = val_str[:-2]
        exec_str += val_str + ");"
        print exec_str
        conn.execute(exec_str)

    conn.commit()

if __name__ == '__main__':
    conn = sqlite3.connect('info.db')
    conn.text_factory = str
    pro_arr = []
    for line in open('pro.list'):
        info = line.strip().split(' ')
        pro_arr.append([info[1], info[2]])
        
    #create_table()
    #insert_table(value=[ "a", "b", "c", "d", "e"])
    #show_table()
    #delete_table("1")
    clean_table()
    #excel_insert()
