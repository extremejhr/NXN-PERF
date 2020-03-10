import sys

sys.path.append('../bin/')

import database_set_new
import database_init
import pandas as pd
import importlib
from peewee import *


class DataGenerator(object):

    def __init__(self, tp_name):

        self.tp_name = tp_name

        database_init.database_connect(self.tp_name)

        importlib.reload(database_set_new)

        self.database = database_set_new.DatabaseTable(self.tp_name)

        self.key_dict = self.database.db_read_init()

    def table_extract(self, table):

        cols = self.key_dict[table]

        dt = eval("self.database." + table + ".select()")

        data = {}

        for col in cols:

            dc = []

            for row in dt:

                dc.append(eval('row.' + col))

            data[col] = dc

        df = pd.DataFrame(data)

        return df

    def db_read_filter(self, table, search_key):

        target_and = ""

        cmd_prefix = "self." + table + ".select().where("

        for group in search_key:

            target_or = ""

            for item in group:

                if len(target_or) == 0:

                    target_or = "(self." + table + "." + item[0] + " == '" + item[1] + "')"

                else:

                    target_or = target_or + ' | ' + "(self." + table + "." + item[0] + " == '" + item[1] + "')"

            if len(group) > 1:

                target_or = '(' + target_or + ')'

            if len(target_and) == 0:

                target_and = target_or

            else:

                target_and = target_and + ' & ' + target_or

        cmd_postfix = ")"

        cmd = cmd_prefix + target_and + cmd_postfix

        data = eval(cmd)

        out_index = print_key

        out_str = ''

        for i in out_index:

            if len(out_str) > 0:

                out_str = out_str + ',' + "value." + i

            else:

                out_str = "value." + i

        cmd = "out.append([" + out_str + "])"

        out = []

        for value in data:

            eval(cmd)

        return out

    def db_distinct(self, table, filter_key):

        cmd = "self." + table + ".select(self." + table + "." + filter_key + ").distinct()"

        distinct = eval(cmd)

        dlist = []

        for item in distinct:

            cmdp = "dlist.append(item." + filter_key + ")"

            eval(cmdp)

        return dlist

