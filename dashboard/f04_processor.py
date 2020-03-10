import re
import datetime


def module_time_extract(lines):

    whole_results = []

    a = set()

    results = {}

    line_stack = lines

    elapsed_time, date = others_time(line_stack)

    line_process = line_preprocess(line_stack)

    submodule_list, list_com = module_line_extract(line_process)

    module_time = mainmodule_time(line_process, list_com)

    results['ELAPSED'] = elapsed_time

    results['DATE'] = date

    results['MAIN'] = module_time

    list_dict = {}

    for sub in submodule_list:

        if sub[0] not in list_dict.keys():

            list_dict[sub[0]] = module_seperate(line_process, range(sub[1] + 1, sub[2]), 1)

        else:

            list_dict[sub[0]] = list_dict[sub[0]] + module_seperate(line_process,
                                                                         range(sub[1] + 1, sub[2]), 1)

    for key in list_dict.keys():

        if len(list_dict[key]) > 0:

            submodule_time_out = submodule_time(line_process, list_dict[key])

            results[key] = submodule_time_out

    whole_results.append(results)

    return whole_results


def line_preprocess(line_stack):

    line = []

    line_process = []

    for i in range(len(line_stack)):

        line_stack[i] = line_stack[i].replace('\n', '').replace('*', '').strip()

        for rep_str in ['BGN', 'BEGN', 'END']:

            line_stack[i] = line_stack[i].replace(rep_str, '  ' + rep_str)

        if re.search(r'^[0-9]+:[0-9]+:[0-9]+', line_stack[i]) is not None:

            line.append(line_stack[i])

            line_sep = line_stack[i].split()

            line_process.append(line_sep)

    return line_process


def module_seperate(line_process, span_list, flag):

    list_dict_bgn = {}

    list_com = []

    for i in span_list:

        if 'BEGN' in line_process[i]:

            index = line_process[i].index('BEGN')

            list_dict_bgn[line_process[i][index-1]] = i

        if flag == 1:

            if 'BGN' in line_process[i]:

                index = line_process[i].index('BGN')

                list_dict_bgn[line_process[i][index - 1]] = i

        if 'END' in line_process[i]:

            index = line_process[i].index('END')

            if line_process[i][index-1] in list_dict_bgn.keys():

                list_com.append([line_process[i][index-1], list_dict_bgn[line_process[i][index-1]], i])

    return list_com


def module_line_extract(line_process):

    submodule_list = []

    module_list = []

    list_com = module_seperate(line_process, range(len(line_process)), 0)

    for i in range(len(list_com)):

        if (list_com[i][2] - list_com[i][1]) > 1:

            submodule_list.append([list_com[i][0], list_com[i][1], list_com[i][2]])

            for linu in range(list_com[i][1]+1, list_com[i][2]):

                module_list.append(linu)

    whole_set = set(range(len(line_process)))

    submodule_set = set(module_list)

    list_com1 = module_seperate(line_process, list(whole_set - submodule_set), 1)

    return submodule_list, list_com1


def mainmodule_time(line, list_dict_com):

    module_time = {}

    total_time = []

    for module in list_dict_com:

        ## Skip MPYAD/VECPLOT

        if module[0] != 'MPYAD':

            start_time = float(line[module[1]][4])

            end_time = float(line[module[2]][4])

            cpu_delta = round(end_time - start_time, 2)

            start_elapsed = line[module[1]][1].split(':')

            end_elapsed = line[module[2]][1].split(':')

            start_time1 = float(start_elapsed[0]) * 60 + float(start_elapsed[1])

            end_time1 = float(end_elapsed[0]) * 60 + float(end_elapsed[1])

            elapsed_delta = end_time1 - start_time1

            if abs(cpu_delta-elapsed_delta) <= 1:

                delta_time = cpu_delta

            else:

                delta_time = elapsed_delta

            total_time.append(delta_time)

            if module[0] in module_time.keys():

                module_time[module[0]] = module_time[module[0]] + delta_time

            else:

                module_time[module[0]] = delta_time

    return module_time


def submodule_time(line, list_dict_com):

    module_time = {}

    total_time = []

    for module in list_dict_com:

        start_time = float(line[module[2]-1][4])

        end_time = float(line[module[2]][4])

        cpu_delta = round(end_time - start_time, 2)

        start_elapsed = line[module[2]-1][1].split(':')

        end_elapsed = line[module[2]][1].split(':')

        start_time1 = float(start_elapsed[0]) * 60 + float(start_elapsed[1])

        end_time1 = float(end_elapsed[0]) * 60 + float(end_elapsed[1])

        elapsed_delta = round(end_time1 - start_time1, 2)

        if abs(cpu_delta-elapsed_delta) <= 1:

            delta_time = cpu_delta

        else:

            delta_time = elapsed_delta

        total_time.append(delta_time)

        if module[0] in module_time.keys():

            module_time[module[0]] = round(module_time[module[0]] + delta_time, 2)

        else:

            module_time[module[0]] = round(delta_time, 2)

    return module_time


def others_time(line):

    for i in range(len(line)-1):

        if 'EXIT' in line[i]:

            line_sep = line[i].strip().split()

            if re.search(r'[0-9]+:[0-9]+:[0-9]+', line_sep[0]) is not None:

                etime = line_sep[1].split(':')

                elapsed_time = int(etime[0])*60 + int(etime[1])

                end_time = line_sep[0]

        if 'RUN DATE' in line[i]:

            date = re.findall(r'\w+\s+\w+,\s+\w+', line[i+1])[-1]

    a = datetime.datetime.strptime(date + ', ' + end_time, '%b %d, %Y, %H:%M:%S')

    return elapsed_time, a
