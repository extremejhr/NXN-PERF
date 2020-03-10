import globalvar as gl
import re
import os
from peewee import *

gl._init()


def setenvvars():

    env_dist = os.environ

    env_dist.get('PERF_PREFIX')

    current_path = env_dist['PERF_PREFIX']

    print(current_path)

    config = open(current_path + '/etc/default_path.cfg')

    database_conf = open(current_path + '/etc/mysql.cfg')

    database_dict = {}

    for line in config.readlines():

        if re.search(r'^$', line) is None:

            vars = re.split(r'=', re.sub(r'\s+', '', line))

            if vars[1][-1] != '/':

                vars[1] = vars[1] + '/'

            if not re.search(r'PREFIX', vars[1]) is None:

                vars[1] = vars[1].replace('${PREFIX}', current_path)

            gl.set_value(vars[0], vars[1])

            #print(gl.get_value(vars[0]))

    for keyvalue in database_conf.readlines():

        if (re.search(r'^#', keyvalue) is None) and (re.search(r'^$', keyvalue) is None):

            vars = re.split(r'=', re.sub(r'\s+', '', keyvalue))

            database_dict[vars[0]] = vars[1]

    gl.set_value('DATABASE', database_dict)

    plans = os.listdir(gl.get_value('TEST_PLAN_PATH'))

    gl.set_value('TABLE', plans[0].split('.')[0])

    db = MySQLDatabase('baseline',
                       user=gl.get_value('DATABASE')['user'],
                       password=gl.get_value('DATABASE')['passwd'],
                       host=gl.get_value('DATABASE')['host'], port=3306)

    gl.set_value('DATABASE_CONNECTION', db)



