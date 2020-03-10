import globalvar as gl
from peewee import *
import pymysql
import var_init
var_init.setenvvars()


def database_connect(database_name):

    try:

        gl.set_value('DATABASE_CONNECTION', None)

    except:

        pass

    print('stop here')

    conn = pymysql.connect(host='172.18.0.1', user='root',
                           password='13848886778jhr')

    cursor = conn.cursor()

    # For Testing

    #sql_del = "DROP DATABASE IF EXISTS" + ' ' + database_name

    #cursor.execute(sql_del)

    #

    sql = "CREATE DATABASE IF NOT EXISTS" + ' ' + database_name

    try:

        cursor.execute(sql)

    except:

        pass

    db = MySQLDatabase(database_name, host='172.18.0.1', user='root',
                           password='13848886778jhr', port=3306)

    gl.set_value('DATABASE_CONNECTION', db)

