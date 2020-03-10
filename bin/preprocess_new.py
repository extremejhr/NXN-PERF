import re
import os
import globalvar as gl
import shutil


class TestPlanPre(object):

    def __init__(self, path):

        self.raw = open(path)

        self.tp_name = re.split(r'/', path)[-1].replace('.tp', '')

        if not os.path.exists(gl.get_value('GROUP_BAK_PATH')):

            os.mkdir(gl.get_value('GROUP_BAK_PATH'))

        if not os.path.exists(gl.get_value('SCRATCH_PATH')):

            os.mkdir(gl.get_value('SCRATCH_PATH'))

        else:

            shutil.rmtree(gl.get_value('SCRATCH_PATH'))

        if not os.path.exists(gl.get_value('RESULT_PATH')):

            os.mkdir(gl.get_value('RESULT_PATH'))

        #else:

        #    shutil.rmtree(gl.get_value('RESULT_PATH'))

        if not os.path.exists(gl.get_value('OUT_CASE_PATH')):

            os.mkdir(gl.get_value('OUT_CASE_PATH'))

        else:

            for file in os.listdir(gl.get_value('OUT_CASE_PATH')):

                if file.endswith('.dat'):

                    os.remove(gl.get_value('OUT_CASE_PATH') + file)

        if not os.path.exists(gl.get_value('SEQUENCE_FILE_PATH')):

            os.mkdir(gl.get_value('SEQUENCE_FILE_PATH'))

        else:

            if os.path.exists(gl.get_value('SEQUENCE_FILE_PATH') + self.tp_name + '.seq'):

                if os.path.exists(gl.get_value('SEQUENCE_FILE_PATH') + self.tp_name + '.seq.bak'):

                    os.remove(gl.get_value('SEQUENCE_FILE_PATH') + self.tp_name + '.seq.bak')

                os.rename(gl.get_value('SEQUENCE_FILE_PATH') + self.tp_name + '.seq',
                          gl.get_value('SEQUENCE_FILE_PATH') + self.tp_name + '.seq.bak')

    def case_modification(self, perf_check, index):

        template_name = index[:-5]

        template_name_all = 'nxnperf_' + template_name

        template = open(gl.get_value('TEMPLATE_PATH') + template_name_all + '.dat')

        out = open(gl.get_value('OUT_CASE_PATH') + self.tp_name + '_' + index + '.dat', 'w')

        if not os.path.exists(gl.get_value('OUT_CASE_PATH') + 'element_' + template_name + '.dat'):

            shutil.copy(gl.get_value('TEMPLATE_PATH') + 'element_' + template_name + '.dat',
                        gl.get_value('OUT_CASE_PATH') + 'element_' + template_name + '.dat')

        for line in template.readlines():

            if not re.search(r'\$PERF_CHECK_[0-9]', line, re.I) is None:

                check_nm = re.search(r'[0-9]', line).group()

                try:

                    line = re.sub(r'\$PERF_CHECK_' + str(check_nm), perf_check[int(check_nm)], line)

                except Exception:

                    line = line

            out.writelines(line)

        out.close()

        return self.tp_name + '_' + index

    def group_build(self, group_version):

        group_folder = 'GROUP_' + group_version

        if group_folder not in os.listdir(gl.get_value('GROUP_BAK_PATH')):

           #os.mkdir(gl.get_value('GROUP_BAK_PATH') + group_folder)

           group_sep = re.split(r'\.', group_version)

           shutil.copytree(gl.get_value('GROUP_BUILD_PATH') + 'DE' + group_sep[0] + 'S/',
                           gl.get_value('GROUP_BAK_PATH') + group_folder + '/DE' + group_sep[0] + 'S/')

           #gl.set_value('GROUP_RUN_PATH',  gl.get_value('GROUP_BAK_PATH') + group_folder + '/bin/nastran')

           rte_build_path = gl.get_value('GROUP_RTE_PATH') + group_version + '/em64tL/'

           rte_local_path = gl.get_value('GROUP_BAK_PATH') + group_folder + '/rte/'

           os.mkdir(rte_local_path)

           shutil.copy(rte_build_path + 'analysis', rte_local_path)

           shutil.copy(rte_build_path + 'SSS.MASTERA', rte_local_path)

           shutil.copy(rte_build_path + 'SSS.MSCOBJ', rte_local_path)

           shutil.copy(rte_build_path + 'SSS.MSCSOU', rte_local_path)

    def sequence_generated(self, case, name):

        seq_file = open(gl.get_value('SEQUENCE_FILE_PATH') + self.tp_name + '.seq', 'a')

        group_version = re.split(r'\.', case['GROUP'])[0]

        solver_run = gl.get_value('GROUP_BAK_PATH') + 'GROUP_' + case['GROUP'] + '/DE' + group_version + 'S/bin/nastran'

        case_name = gl.get_value('OUT_CASE_PATH') + 'nxnperf_' + name

        print('nxnperf_' + name, ' is generated ...')

        group_folder = 'GROUP_' + case['GROUP']

        rte_local_path = gl.get_value('GROUP_BAK_PATH') + group_folder + '/rte/'

        rte_cmd = 'exe=' + rte_local_path + 'analysis' + ' del=' + rte_local_path + 'SSS'

        env_cmd = 'sdirectory=' + gl.get_value('SCRATCH_PATH') + ' dbs=' + gl.get_value('SCRATCH_PATH') \
                  + ' scratch=no' + ' batch=no' + ' out=' + name

        for cmds in case['COMMAND']:

            env_cmd = env_cmd + ' ' + cmds

        line = solver_run + ' ' + case_name + ' ' + rte_cmd + ' ' +env_cmd + '\n'

        seq_file.writelines(line)

        seq_file.close()

    def plan_format(self):

        case_info =[]

        for line in self.raw.readlines():

            if re.search(r'^#!', line) is not None:

                bulk_key = line.replace('#!', '').replace('\n', '').split(',')

            if (re.search(r'^$', line) is None) and (re.search(r'^#', line) is None):

                line_sep = re.split(r'\]\s*\[', re.sub(r'^\].*', '', line.strip()[1:-1]))

                case = {}

                for paras in line_sep:

                    sets = re.split(':', paras)

                    if sets[0].upper() == 'TEMPLATE':

                        template_name = sets[1]

                        case['TEMPLATE'] = template_name

                    elif sets[0].upper() == 'GROUP':

                        group_version = sets[1]

                        case['GROUP'] = group_version

                    elif sets[0].upper() == 'COMMAND':

                        commands = re.split(r'\s+', sets[1])

                        case['COMMAND'] = commands

                    elif sets[0].upper() == 'BULK_DATA':

                        perf_chk_nm = []

                        perf_chk_bulk = []

                        for bulk in re.split(r'\$', sets[1])[1:]:

                            bulk1 = re.search(r'\{[0-9]\}', bulk).group()[1]		

                            bulk2 = bulk[3:]	    

                            perf_chk_nm.append(int(bulk1))

                            perf_chk_bulk.append(bulk2)

                        perf_check = [[]] * len(perf_chk_nm)

                        for i in range(len(perf_chk_nm)):

                            perf_check[perf_chk_nm[i]] = perf_chk_bulk[i]

                        case['BULK'] = perf_check

                    else:

                        print('Wrong Test Plan Keyword!')

                case_info.append(case)

        key = {}

        key_plan = ['DATE', 'CASE', 'GROUP', 'RESULT', 'ELAPSED']

        key_case = ['CASE', 'TEMPLATE']

        key_result = ['RESULT', 'MAIN', 'NLTRD3']

        key_result_main = ['MAIN']

        key_result_nltrd3 = ['NLTRD3']

        #key_result_vecplot = ['VECPLOT']

        a = set()

        for case in case_info:

            com = []

            for cmds in case['COMMAND']:

                com.append(cmds.split('=')[0].upper())

            a = a | set(com)

        key_case = key_case + list(a)

        for bulks in bulk_key:

            key_case.append(bulks)

        key['plan'] = key_plan
        key['case'] = key_case
        key['result'] = key_result
        key['main'] = key_result_main
        key['nltrd3'] = key_result_nltrd3
        #key['vecplot'] = key_result_vecplot

        return case_info, key, bulk_key

    def setup(self, case_info, name_list):

        file_list = []

        for index in name_list:

            name = self.case_modification(case_info[index[0]]['BULK'], index[1])

            self.sequence_generated(case_info[index[0]], name)

            #self.group_build(case_info[index[0]]['GROUP'])

            file_list.append(name)

        return file_list




