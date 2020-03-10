import var_init
import preprocess_new
import postprocess_new
import database_init
import importlib
import database_set_new

var_init.setenvvars()

test_plan_list = ['baseline']

for test_plan in test_plan_list:

    preprocessor = preprocess_new.TestPlanPre('../test_plan/' + test_plan + '.tp')

    case_info, key, keyword = preprocessor.plan_format()

    database_init.database_connect(test_plan)

    importlib.reload(database_set_new)

    database1 = database_set_new.DatabaseTable(test_plan)

    database1.db_crt_preinit(key)

    name_list = database1.db_key_premap(case_info, keyword)

    file_list = preprocessor.setup(case_info, name_list)

    # RUN SEQUENCE

    if len(name_list) > 0:

        postprocessor = postprocess_new.CaseResult(file_list)

        results = postprocessor.module_time_extract()

        database1.db_crt_postinit(key, results)

        data = database1.db_key_postmap(results, file_list)


