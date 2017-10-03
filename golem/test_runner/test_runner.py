"""
This module contains the method for running one test
"""
import sys
import importlib
import time
import traceback

import golem.core
from golem.core import report, utils


def run_test(workspace, project, test_name, test_data, driver,
             settings, report_directory):
    ''' runs a single test case by name'''
    result = {
        'result': 'pass',
        'error': '',
        'description': '',
        'steps': [],
        'test_elapsed_time': None,
        'test_timestamp': None,
        'browser': driver
    }

    from golem.core import execution_logger
    from golem import actions
    from golem import execution

    # convert test_data to data obj
    class Data:
        def __init__(self, data):
            for key, value in data.items():
                setattr(self, key, value)

    execution.data = Data(test_data)

    logger = execution_logger.get_logger(report_directory,
                                         settings['console_log_level'],
                                         settings['file_log_level'],
                                         settings['log_all_events'])
    execution.logger = logger

    logger.info('Test execution started: {}'.format(test_name))
    logger.info('Driver: {}'.format(driver))
    if test_data:
        data_string = '\n'
        for key, value in test_data.items():
            data_string += '    {}: {}\n'.format(key, value)
        logger.info('Using data: {}'.format(data_string))

    test_timestamp = utils.get_timestamp()
    test_start_time = time.time()

    execution.project = project
    execution.workspace = workspace
    execution.driver_name = driver
    execution.settings = settings
    execution.report_directory = report_directory

    test_module = None

    try:
        test_module = importlib.import_module(
            'projects.{0}.tests.{1}'.format(project, test_name))

        # import the page objects into the test module
        if hasattr(test_module, 'pages'):
            for page in test_module.pages:
                test_module = utils.generate_page_object_module(project, test_module,
                                                                page, page.split('.'))

        # import logger into the test module
        setattr(test_module, 'logger', execution.logger)

        # import actions into the test module
        for action in dir(golem.actions):
            setattr(test_module, action, getattr(golem.actions, action))

        # log description
        if hasattr(test_module, 'description'):
            execution.description = test_module.description
        else:
            logger.info('Test does not have description')

        # run setup method
        if hasattr(test_module, 'setup'):
            test_module.setup(execution.data)
        else:
            logger.info('Test does not have setup function')

        if hasattr(test_module, 'test'):
            test_module.test(execution.data)
        else:
            raise Exception('Test does not have test function')
    except:
        result['result'] = 'fail'
        result['error'] = traceback.format_exc()
        try:
            if settings['screenshot_on_error'] and execution.driver:
                actions.capture('error')
        except:
            # if the test failed and driver is not available
            # capture screenshot is not possible, continue
            pass

        logger.error('An error ocurred:', exc_info=True)

    try:
        if hasattr(test_module, 'teardown'):
            test_module.teardown(execution.data)
        else:
            logger().info('Test does not have a teardown function')
    except:
        result['result'] = 'fail'
        result['error'] += '\n\nteardown failed'
        result['error'] += '\n' + traceback.format_exc()
        logger.error('An error ocurred in the teardown:', exc_info=True)

    # if there is no teardown or teardown failed or it did not close the driver,
    # let's try to close the driver manually
    if execution.driver:
        try:
            execution.driver.quit()
        except:
            # if this fails, we have lost control over the webdriver window
            # and we are not going to be able to close it
            logger.error('There was an error closing the driver')
            logger.error(traceback.format_exc())
        finally:
            execution.driver = None

    test_end_time = time.time()
    test_elapsed_time = round(test_end_time - test_start_time, 2)

    if not result['error']:
        logger.info('Test passed')

    result['description'] = execution.description
    result['steps'] = execution.steps
    result['test_elapsed_time'] = test_elapsed_time
    result['test_timestamp'] = test_timestamp
    result['browser'] = execution.driver_name

    # remove golem.execution from sys.modules to guarantee thread safety
    #sys.modules['golem.execution'] = None
    del sys.modules['golem.execution']
    report.generate_report(report_directory, test_name, execution.data, result)
    return
