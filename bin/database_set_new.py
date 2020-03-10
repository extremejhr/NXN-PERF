from peewee import *
import globalvar as gl
import datetime
import var_init

var_init.setenvvars()


class DatabaseTable(object):

    def __init__(self, tp):

        self.name = tp

        self.tp_name = tp

        self.Result = type(self.name + '_Result', (self.BaseModel,), {})

        self.Main = type(self.name + '_Main', (self.BaseModel,), {})

        self.Nltrd3 = type(self.name + '_Nltrd3', (self.BaseModel,), {})

        self.Vecplot = type(self.name + '_Vecplot', (self.BaseModel,), {})

        self.Case = type(self.name + '_Case', (self.BaseModel,), {})

        self.Plan = type(self.name + '_Plan', (self.BaseModel,), {})

    class BaseModel(Model):
        class Meta:
            database = gl.get_value('DATABASE_CONNECTION')

    class KeySet(BaseModel):

        name = CharField(max_length=50, default='None', primary_key=True)

        key = CharField(max_length=5000, default='None')

        class Meta:

            db_table = 'keyset'

    def key_merge(self, key_name, merge_item):

        try:

            key_search = self.KeySet.select().where(self.KeySet.name == key_name)

            key_tmp = set(key_search[0].key.split(','))

        except Exception:

            key_search = ''

            key_tmp = set()

        module_out = list(key_tmp | set(merge_item))

        keyin = ''

        for item in module_out:

            if len(keyin) > 0:

                keyin = keyin + ',' + item

            else:

                keyin = item

        if len(key_tmp) > 0:

            self.KeySet.update({self.KeySet.key: keyin}).where(self.KeySet.name == key_name).execute()

        else:

            self.KeySet.insert({self.KeySet.key: keyin, self.KeySet.name: key_name}).execute()


        #out = self.KeySet.select().where(self.KeySet.name == key_name)[0].key

        #print(out.split(','))

        return module_out

    def db_crt_preinit(self, key):

        self.KeySet.create_table()

        case_out = self.key_merge('key_case', key['case'])

        for item in case_out:

            self.Case._meta.add_field(item, CharField(max_length=50, default='X'))

        self.Case.create_table()

        plan_out = self.key_merge('key_plan', key['plan'])

        for item in plan_out:

            if item == 'DATE':

                self.Plan._meta.add_field(item, DateTimeField(default=datetime.datetime.now()))

            elif item == 'ELAPSED':

                self.Plan._meta.add_field(item, FloatField(default=0.0))

            else:

                self.Plan._meta.add_field(item, CharField(max_length=50, default='None'))

        self.Plan.create_table()

        result_out = self.key_merge('key_result', key['result'])

        for item in result_out:

            self.Result._meta.add_field(item, CharField(max_length=50, default='None'))

        self.Result.create_table()

    def db_crt_postinit(self, key, result_set):

        #self.KeySet.create_table()

        for results in result_set:

            key1 = {}

            module_main = results['MAIN'].keys()

            module_nltrd3 = results['NLTRD3'].keys()

            #module_vecplot = results['VECPLOT'].keys()

            key1['main'] = key['main'] + list(module_main)

            key1['nltrd3'] = key['nltrd3'] + list(module_nltrd3)

            #key['vecplot'] = key['vecplot'] + list(module_vecplot)

            main_out = self.key_merge('key_main', key1['main'])

            nltrd3_out = self.key_merge('key_nltrd3', key1['nltrd3'])

            #vecplot_out = self.key_merge('key_vecplot', key['vecplot'])

        for item in main_out:

            if item == 'MAIN':

                self.Main._meta.add_field(item, CharField(max_length=50, default='None'))

            else:

                self.Main._meta.add_field(item, FloatField(default=0))

        self.Main.create_table()

        for item in nltrd3_out:

            if item == 'NLTRD3':

                self.Nltrd3._meta.add_field(item, CharField(max_length=50, default='None'))

            else:

                self.Nltrd3._meta.add_field(item, FloatField(default=0))

        self.Nltrd3.create_table()

    def db_key_premap(self, case_info, keyword):

        name_list = {}

        td_list = []

        result_index = {}

        ids = {}

        prev_template = []

        index = 0

        for case in case_info:

            value = {}

            value['TEMPLATE'] = case['TEMPLATE']

            if value['TEMPLATE'] not in prev_template:

                ids[value['TEMPLATE']] = 0

                prev_template.append(value['TEMPLATE'])

                result_index[value['TEMPLATE']] = 0

                name_list[value['TEMPLATE']] = []

            for cmd in case['COMMAND']:

                value[cmd.split('=')[0].upper()] = cmd.split('=')[1].upper()

            for dep in keyword:

                for bulk in case['BULK']:

                    if dep in bulk:

                        if ',' in bulk:

                            tmp = bulk.split(',')

                        elif '=' in bulk:

                            tmp = bulk.split('=')

                        else:

                            tmp = bulk

                        value[dep.upper()] = str.strip(tmp[tmp.index(dep)+1]).upper()

            pk = ''

            cname = ''

            for key1 in value.keys():

                pk = 'self.Case.' + key1 + "=='" + value[key1] + "'," + pk

                cname = value[key1] + cname

            a = eval('self.Case.select().where(' + pk[:-1] + ')')

            if not a.exists():

                #ids = self.Case.select(self.Case.id)

                value['CASE'] = value['TEMPLATE'].upper()

                for vk in value.keys():

                    if vk != 'CASE' and vk != 'TEMPLATE' and vk != 'MEM':

                        if len(vk) >= 3:

                            postfix = vk[:3]

                        else:

                            postfix = vk

                        value['CASE'] = value['CASE'] + '_' + postfix.upper() + value[vk].upper()

                self.Case.insert_many(value).execute()

                ids[value['TEMPLATE']] = ids[value['TEMPLATE']] + 1

            case_id = eval('self.Case.select().where(' + pk[:-1] + ')')[0].CASE

            b = self.Plan.select().where(self.Plan.CASE == case_id, self.Plan.GROUP == case['GROUP'])

            if not b.exists():

                id_sum = self.Plan.select().count()

                self.Plan.insert_many({self.Plan.CASE: case_id,
                                       self.Plan.GROUP: case['GROUP'],
                                       self.Plan.RESULT: self.tp_name + '_' + value['TEMPLATE'] + '_' +
                                                         str(id_sum + 1 + 10000)[1:]}
                                      ).execute()

                #ids[value['TEMPLATE']] = ids[value['TEMPLATE']] + 1

                #name_list[value['TEMPLATE']].append(str(result_index[value['TEMPLATE']] + 1000)[1:])

                td_list.append([index, value['TEMPLATE'] + '_' + str(id_sum + 1 + 10000)[1:]])

            result_index[value['TEMPLATE']] = result_index[value['TEMPLATE']] + 1

            index = index + 1

            print(td_list)

        return td_list

    def db_key_postmap(self, results, file_list):

        index = 0

        for post in results:

            date = post['DATE']

            elapsed = post['ELAPSED']

            data = post.copy()

            result = {'RESULT': file_list[index], 'MAIN': file_list[index], 'NLTRD3': file_list[index]}

            main = data['MAIN']

            main['MAIN'] = file_list[index]

            nltrd3 = data['NLTRD3']

            nltrd3['NLTRD3'] = file_list[index]

            data['RESULT'] = file_list[index]

            self.Plan.update({'DATE': date}).where(self.Plan.RESULT == file_list[index]).execute()

            self.Plan.update({'ELAPSED': elapsed}).where(self.Plan.RESULT == file_list[index]).execute()

            self.Result.insert_many(result).execute()

            self.Main.insert_many(main).execute()

            self.Nltrd3.insert_many(nltrd3).execute()

            index = index + 1

    def db_read_init(self):

        key_case = self.KeySet.select().where(self.KeySet.name == 'key_case')[0].key.split(',')

        key_result = self.KeySet.select().where(self.KeySet.name == 'key_result')[0].key.split(',')

        key_plan = self.KeySet.select().where(self.KeySet.name == 'key_plan')[0].key.split(',')

        key_main = self.KeySet.select().where(self.KeySet.name == 'key_main')[0].key.split(',')

        key_nltrd3 = self.KeySet.select().where(self.KeySet.name == 'key_nltrd3')[0].key.split(',')

        for item in key_case:

            self.Case._meta.add_field(item, CharField(max_length=50, default='X'))

        for item in key_plan:

            if item == 'DATE':

                self.Plan._meta.add_field(item, DateTimeField(default=datetime.datetime.now()))

            elif item == 'ELAPSED':

                self.Plan._meta.add_field(item, FloatField(default=0.0))

            else:

                self.Plan._meta.add_field(item, CharField(max_length=50, default='None'))

        for item in key_result:

                self.Result._meta.add_field(item, CharField(max_length=50, default='None'))

        for item in key_main:

            if item == 'MAIN':

                self.Main._meta.add_field(item, CharField(max_length=50, default='None'))

            else:

                self.Main._meta.add_field(item, FloatField(default=0))

        for item in key_nltrd3:

            if item == 'NLTRD3':

                self.Nltrd3._meta.add_field(item, CharField(max_length=50, default='None'))

            else:

                self.Nltrd3._meta.add_field(item, FloatField(default=0))

        return {'Case': key_case, 'Result': key_result, 'Plan': key_plan, 'Main': key_main, 'Nltrd3': key_nltrd3}













