# -*- coding: UTF-8 -*-
from __future__ import division
import sys
import json
import os
import sqlite3
import xlrd
import xlwt
import time
import datetime
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask, render_template, jsonify, request, redirect, url_for, send_from_directory, make_response , send_file
from werkzeug import secure_filename
from flask_bootstrap import Bootstrap

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['xls', 'xlsx', 'txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bootstrap = Bootstrap(app)

conn = sqlite3.connect('info.db')

pro_arr = []
for line in open('pro.list'):
    info = line.strip().split(' ')
    cn_name = info[0]
    en_name = info[1]
    log_type = info[3]
    pro_arr.append([cn_name, en_name, log_type])

author = 'staff-1'

login_info = {
    'is_login': 0,
    'login_name': '',
}

user_info = [
        ['Admin-1', 'adm123456']
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def insert_db(value_info={}):
    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    exec_str = "INSERT INTO main_info VALUES ("
    val_str = 'NULL, '

    for item in pro_arr:
        val_str += '"' + value_info[item[1]] + '", '
    val_str = val_str[:-2]
    exec_str += val_str + ");"
    conn.execute(exec_str)


    exec_str = "INSERT INTO log_info VALUES ("
    val_str = 'NULL, '
    for item in pro_arr:
        val_str += '"' + value_info[item[1]] + '", '
        val_str += 'NULL, '
    val_str += '"' + cur_time + '",'
    val_str += '"' + author + '",'
    val_str += '"insert"'
    exec_str += val_str + ");"
    conn.execute(exec_str)

def update_db(id='', old_pro={}, new_pro={}):
    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    exec_str  = "UPDATE main_info SET "
    value_str = ""
    for item in pro_arr:
        value_str += item[1] + " = " + '"' + new_pro[item[1]] + '",'
    value_str = value_str[:-1]
    exec_str += value_str
    exec_str += " WHERE id = " + id
    print exec_str

    conn.execute(exec_str)

    exec_str = "INSERT INTO log_info VALUES ("
    val_str = 'NULL, '
    for item in pro_arr:
        val_str += '"' + new_pro[item[1]] + '", '
        val_str += '"' + old_pro[item[1]] + '", '
    val_str += '"' + cur_time + '",'
    val_str += '"' + author + '",'
    val_str += '"update"'
    exec_str += val_str + ");"
    conn.execute(exec_str)

def delete_db(id='', old_pro={}):
    cur_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    exec_str = "DELETE FROM main_info WHERE id = "+id+";"
    conn.execute(exec_str)

    exec_str = "INSERT INTO log_info VALUES ("
    val_str = 'NULL, '
    for item in pro_arr:
        val_str += 'NULL, '
        val_str += '"' + old_pro[item[1]] + '", '
    val_str += '"' + cur_time + '",'
    val_str += '"' + author + '",'
    val_str += '"delete"'
    exec_str += val_str + ");"
    conn.execute(exec_str)


@app.route('/save_file', methods=['GET', 'POST'])
def save_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            work_book = xlrd.open_workbook('uploads/' + filename)
            sh = work_book.sheet_by_index(0)
            for idx_row in range(sh.nrows):
                value_info = {}
                for i in range(0, len(sh.row(idx_row))):
                    pro_name = pro_arr[i][1]
                    pro_item = sh.row(idx_row)[i]

                    #pro_value = sh.row(idx_row)[i].value
                    #if sheet.cell(5, 19).ctype == 3:
                    pro_type = pro_item.ctype
                    if pro_type == 1:
                        pro_value = pro_item.value.encode('utf8')
                    elif pro_type == 2:
                        pro_value = str(int(pro_item.value))
                    elif pro_type == 3:
                        ms_date_number = pro_item.value
                        year, month, day, hour, minute, second = xlrd.xldate_as_tuple(ms_date_number, work_book.datemode)
                        t = (year, month, day, hour, minute, second, 0, 0, 0)
                        t = time.mktime(t)
                        pro_value = time.strftime('%Y/%m/%d', time.gmtime(t))
                        #print pro_value
                    #pro_value = str(pro_value).encode('utf8')
                    value_info[pro_name] = pro_value
                insert_db(value_info)
            conn.commit()
            print sh.nrows
            #return redirect(url_for('uploaded_file',filename=filename))
            return redirect(url_for('update_res', num=sh.nrows, login_info=login_info))

@app.route('/update_res/<num>')
def update_res(num):
    if login_info['is_login'] == 0:
        return redirect(url_for('retrieve', pro_arr=pro_arr, login_info=login_info))
    return render_template('update_res.html', num=num, login_info=login_info)

@app.route('/update_save', methods=['GET', 'POST'])
def update_save():
    if request.method == 'POST':
        id = request.form['id']
        new_dict = {}
        old_dict = {}
        for item in pro_arr:
            new_dict[item[1]] = request.form[item[1] + '_new']
            old_dict[item[1]] = request.form[item[1] + '_old']

        update_db(id=id, old_pro=old_dict, new_pro=new_dict)
        conn.commit()
        return '1'

@app.route('/insert_save', methods=['GET', 'POST'])
def insert_save():
    if request.method == 'POST':
        info_dict = {}
        for item in pro_arr:
            info_dict[item[1]] = request.form[item[1]]
        insert_db(value_info=info_dict)
        conn.commit()
        return '1'

@app.route('/delete_save', methods=['GET', 'POST'])
def delete_save():
    if request.method == 'POST':
        info_dict = {}
        id = request.form['id']
        print id
        for item in pro_arr:
            info_dict[item[1]] = request.form[item[1]]
        delete_db(id=id, old_pro=info_dict)
        conn.commit()
        return '1'


@app.route('/', methods=['GET', 'POST'])
def uploads_file():
    if login_info['is_login'] == 0:
        return redirect(url_for('retrieve', pro_arr=pro_arr, login_info=login_info))
    return render_template('uploads.html', login_info=login_info)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)


@app.route('/edit')
def edit():
    if login_info['is_login'] == 0:
        return redirect(url_for('retrieve', pro_arr=pro_arr, login_info=login_info))
    info_arr = []
    cursor = conn.execute("SELECT * FROM main_info")
    for row in cursor:
        info = {}
        info['id'] = row[0]
        for i in range(1, len(row)):
            pro_name = pro_arr[i-1][1]
            info[pro_name] = row[i]
        info_arr.append(info)

    return render_template('edit.html', pro_arr=pro_arr, info_arr=info_arr, login_info=login_info)

@app.route('/log')
def log():
    if login_info['is_login'] == 0:
        return redirect(url_for('retrieve', pro_arr=pro_arr, login_info=login_info))
    info_arr = []
    cursor = conn.execute("SELECT * FROM log_info")
    for row in cursor:
        info = {}
        info['id'] = row[0]
        row_len = len(row)
        for i in range(1, row_len-3):
            if i % 2 == 1:
                pro_name = pro_arr[int((i-1)/2)][1] + '_new'
            else:
                pro_name = pro_arr[int((i-2)/2)][1] + '_old'
            info[pro_name] = row[i]
        info['insert_time'] = row[-3]
        info['author']      = row[-2]
        info['type']        = row[-1]
        info_arr.append(info)
    print info_arr
    return render_template('log.html', pro_arr=pro_arr, info_arr=info_arr, login_info=login_info)


@app.route('/retrieve')
def retrieve():
    return render_template('retrieve.html', pro_arr=pro_arr, login_info=login_info)

@app.route('/info_search', methods=['GET', 'POST'])
def info_search():
    if request.method == 'POST':
        key = request.form['key']

        info_arr = []
        cursor = conn.execute("SELECT * FROM main_info WHERE name LIKE '%"+key+"%'")
        for row in cursor:
            i_info = []
            for item in row:
                i_info.append(item)
            info_arr.append(i_info)
        return json.dumps({'info':info_arr})

@app.route('/get_login', methods=['GET', 'POST'])
def get_login():
    if request.method == 'POST':
        name = request.form['name']
        pwd  = request.form['pwd']

        for item in user_info:
            if item[0] == name and item[1] == pwd:
                login_info['is_login'] = 1
                login_info['login_name'] = item[0]
                return '1'
        return '0'

@app.route('/get_loginout', methods=['GET', 'POST'])
def get_loginout():
    if request.method == 'POST':
        login_info['is_login'] = 0
        return '1'



def set_style(name, height, bold=False):
    style = xlwt.XFStyle()  # 初始化样式

    font = xlwt.Font()  # 为样式创建字体
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.color_index = 4
    font.height = height

    # borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6

    style.font = font
    # style.borders = borders

    return style



@app.route('/export_xml')
def export_xml():
    f = xlwt.Workbook()  # 创建工作簿

    sheet1 = f.add_sheet(u'sheet1', cell_overwrite_ok=True)  # 创建sheet

    cursor = conn.execute("SELECT * FROM main_info")
    index = 0
    for row in cursor:
        for i in range(1, len(row)):
            sheet1.write(index, i-1, row[i], set_style('Times New Roman', 220, True))
        index += 1

    f.save('uploads/export.xls')  # 保存文件

    #if os.path.isfile(os.path.join('uploads', 'cover-5.jpg')):
    #    print 11111
    return send_from_directory('uploads', 'export.xls', as_attachment=True)
    #return 'uploads/sample-test-1-2.xlsx'

@app.route('/testdownload', methods=['GET'])
def testdownload():
    response = make_response(send_file("uploads/sample-test-1-2.xlsx"))
    response.headers["Content-Disposition"] = "attachment; filename=uploads/sample-test-1-2.xlsx;"
    return response


if __name__ == '__main__':
    app.run()
