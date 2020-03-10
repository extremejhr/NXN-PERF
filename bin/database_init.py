import globalvar as gl
from peewee import *
import pymysql


def database_connect(database_name):

    try:

        gl.set_value('DATABASE_CONNECTION', None)

    except:

        pass

    conn = pymysql.connect(host=gl.get_value('DATABASE')['host'], user=gl.get_value('DATABASE')['user'],
                           password=gl.get_value('DATABASE')['passwd'], charset=gl.get_value('DATABASE')['charset'])

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

    db = MySQLDatabase(database_name,
                       user=gl.get_value('DATABASE')['user'],
                       password=gl.get_value('DATABASE')['passwd'],
                       host=gl.get_value('DATABASE')['host'], port=3306)

    gl.set_value('DATABASE_CONNECTION', db)

