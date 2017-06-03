"""
This module contains the methods for running a suite of tests and
a single test case.

The multiprocess_executor method runs all the test cases provided in
parallel using multiprocessing.

The test_runner method is in charge of executing a single test case.
"""

import importlib
import sys
import time
import traceback
from multiprocessing import Pool
from multiprocessing.pool import ApplyResult

import golem.core
from golem.core import (actions,
                        report,
                        test_execution,
                        utils)


def test_runner(workspace, project, test_case_name, test_data, driver, suite_name,
                suite_data, suite_timestamp, settings):
    ''' runs a single test case by name'''
    result = {
        'result': 'pass',
        'error': None,
        'description': None,
        'steps': None,
        'test_elapsed_time': None,
        'test_timestamp': None,
        'browser': driver}

    from golem.core import execution_logger
    ## instance = None
    test_timestamp = utils.get_timestamp()
    test_start_time = time.time()

    golem.core.project = project
    golem.core.workspace = workspace
    golem.core.test_data = test_data
    golem.core.driver_name = driver
    golem.core.set_settings(settings)

    # create a directory to store report.json and screenshots
    report_directory = report.create_report_directory(workspace, project, test_case_name,
                                                      suite_name, suite_timestamp)
    try:
        test_module = importlib.import_module(
            'projects.{0}.test_cases.{1}'.format(project, test_case_name))

        # test_class = utils.get_test_case_class(project,
        #                                        test_case_name)
        # import the page objects into the test module
        for page in test_module.pages:
            test_module = utils.generate_page_object_module(project, test_module, page, page.split('.'))
        # import logger into the test module
        setattr(test_module, 'logger', golem.core.execution_logger)
        # import actions into the test module
        for action in dir(golem.core.actions):
            setattr(test_module, action, getattr(golem.core.actions, action))

        # instance = test_class()
        if hasattr(test_module, 'description'):
            golem.core.execution_logger.description = test_module.description
    
        if hasattr(test_module, 'setup'):
            test_module.setup()
        else:
            raise Exception('Test does not have setup method')
        if hasattr(test_module, 'test'):
            # instance.test(test_data)
            test_module.test(golem.core.test_data)
        else:
            raise Exception('Test does not have test method')

    except:
        result['result'] = 'fail'
        result['error'] = traceback.format_exc()
        try:
            if settings['screenshot_on_error']:
                actions.capture('error')
        except:
            # if the test failed and chrome is not available
            # capture screenshot is not possible, continue
            pass
        print(dir(traceback))
        print(traceback.print_exc())

    try:
        if hasattr(test_module, 'teardown'):
            test_module.teardown()
        else:
            actions.close()
    except:
        result['result'] = 'fail'
        result['error'] = 'teardown failed'

    test_end_time = time.time()
    test_elapsed_time = round(test_end_time - test_start_time, 2)

    result['description'] = execution_logger.description
    result['steps'] = execution_logger.steps
    result['test_elapsed_time'] = test_elapsed_time
    result['test_timestamp'] = test_timestamp
    result['screenshots'] = execution_logger.screenshots
    result['browser'] = golem.core.get_selected_driver()

    execution_logger.description = None
    execution_logger.steps = []
    execution_logger.screenshots = {}

    report.generate_report(report_directory,
                           test_case_name,
                           test_data,
                           result)
    return result


def multiprocess_executor(execution_list, processes=1, suite_name=None, suite_data=None):
    print('execution list', execution_list)

    if test_execution.timestamp:
        timestamp = test_execution.timestamp
    else:
        timestamp = utils.get_timestamp()

    pool = Pool(processes=processes)

    results = []
    for test in execution_list:
        args = (test_execution.root_path,
                test_execution.project,
                test['test_case_name'],
                test['data_set'],
                test['driver'],
                suite_name,
                suite_data,
                timestamp,
                test_execution.settings)
        apply_async = pool.apply_async(test_runner, args=args)
        results.append(apply_async)

    map(ApplyResult.wait, results)

    lst_results = [r.get() for r in results]

    # for res in lst_results:
    #    print '\none result\n',res

    pool.close()
    pool.join()


def run_single_test_case(workspace, project, full_test_case_name):

    # check if test case exists
    if not utils.test_case_exists(workspace, project, full_test_case_name):
        sys.exit(
            "ERROR: no test case named {} exists".format(full_test_case_name))
    else:
        threads = 1
        if test_execution.thread_amount:
            threads = test_execution.thread_amount
        
        execution_list = []

        drivers = []

        if test_execution.drivers:
            drivers = test_execution.drivers

        if not drivers and 'default_driver' in test_execution.settings:
            drivers = [test_execution.settings['default_driver']]

        if not drivers:
            drivers = ['firefox']

        # get test data
        data_sets = utils.get_test_data(workspace,
                                        project,
                                        full_test_case_name)
        if not data_sets:
            data_sets = [{}]
        
        for data_set in data_sets:
            for driver in drivers:
                execution_list.append({
                    'test_case_name': full_test_case_name,
                    'data_set': data_set,
                    'driver': driver,
                    })

        # run the single test, once for each data set
        multiprocess_executor(execution_list, threads)


def run_suite(workspace, project, suite, is_directory=False):
    '''run a suite
    a suite can be a python module in "test_suites" directory or
    a first level directory in "test_cases" directory, the latter
    allows the user to run all the test cases inside that directory without
    the need to create a new suite and add the tests to it'''

    # get test case list
    if is_directory:
        test_case_list = utils.get_directory_suite_test_cases(workspace, project, suite)
    else:
        test_case_list = utils.get_suite_test_cases(project, suite)

    threads = 1
    
    suite_file_amount_workers = utils.get_suite_amount_of_workers(workspace, project, suite)
    if suite_file_amount_workers > 1:
        threads = suite_file_amount_workers

    # the thread count pass through cli has higher priority
    if test_execution.thread_amount:
        threads = test_execution.thread_amount

    drivers = []

    suite_file_drivers = utils.get_suite_browsers(workspace, project, suite)
    if suite_file_drivers:
        drivers = suite_file_drivers

    if test_execution.drivers:
        drivers = test_execution.drivers

    if not drivers and 'default_driver' in test_execution.settings:
        drivers = [test_execution.settings['default_driver']]

    if not drivers:
        drivers = ['firefox']

    # get test data for each test case present in the suite
    # and append tc/data pairs for each test case and for each data
    # set to execution list.
    # if there is no data for a test case, it is appended with an
    # empty dict
    execution_list = []
    for test_case in test_case_list:
        data_sets = utils.get_test_data(workspace, project, test_case)
        if not data_sets:
            data_sets = [{}]
        for data_set in data_sets:
            for driver in drivers:
                execution_list.append({
                    'test_case_name': test_case,
                    'data_set': data_set,
                    'driver': driver
                    })

    multiprocess_executor(execution_list,
                          threads,
                          suite_name=suite)
