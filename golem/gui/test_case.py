import os
import re

from golem.core import utils
from golem.gui import data, page_object, gui_utils


def _get_steps(content):

    index = -1
    steps = []
    for i, line in enumerate(content): 
        if 'def test(self, data):' in line:
            index = i + 1
            break
    if index >= 0:
        while True:
            current_line = content[index]
            if 'def teardown' in current_line:
                end_of_steps = True
                break
            if len(current_line.strip()) > 0 and current_line.strip() != 'pass':
                #this is a step
                method_name = current_line.split('(')[0].strip()
                parameters = current_line.split('(')[1].split(')')[0]
                parameter_list = [x for x in parameters.split(',')]
                formatted_parameters = []
                for parameter in parameter_list:
                    if '\'' in parameter:
                        formatted_parameters.append(parameter.split('\'')[1])
                    else:
                        formatted_parameters.append(parameter)
                step = {
                    'method_name' : method_name.replace('_', ' '),
                    'parameters' : formatted_parameters
                }
                steps.append(step)
            if 'def teardown' in current_line:
                end_of_steps = True
            index += 1
    return steps


def get_datos(content):
    save_content = False
    datos_lines = []
    for line in content:   
        if save_content and 'pasos' not in line:
            datos_lines.append(line)
        if 'datos' in line:
            save_content = True
        if 'pasos' in line:
            save_content = False
    datos = []
    for line in datos_lines:
        line = line.replace('\t', '')
        if len(line.strip()) > 0:
            variable = line.split(' ')[1]
            datos.append(variable);
    return datos


def get_page_objects(content):

    page_objects = []
    index = -1
    for i, line in enumerate(content):
        if 'page objects' in line:
            index = i + 1
            break
    while not 'class' in content[index]:
        page_object_line = content[index]
        if 'import' in page_object_line:
            page_object = page_object_line.split('import')[1]
            page_objects.append(page_object.strip())
        index += 1
    return page_objects


def get_description(content):

    contentString = ''.join(content)
    description = ''
    index = 0
    description = re.search(
                            ".*description = \'\'\'(.*\n*.*)\'\'\'",
                            contentString
                            ).group(1)
    description = re.sub("\s\s+", " ", description)
    return description


def get_execute_script_content(content):

    execute_script_content = []

    save_content = False
    level = 0
    for line in content:
        if save_content and '{' in line:
            level += 1
        if save_content and '}' in line:
            if level > 0:
                level -= 1
            else:
                save_content = False
        if save_content:
            execute_script_content.append(line)
        if 'executeScript' in line:
            save_content = True
    return execute_script_content


def parse_test_case(workspace, project, parents, test_case_name):

    parents_joined = os.sep.join(parents)

    path = os.path.join(
                        workspace,
                        'projects',
                        project,
                        'test_cases',
                        parents_joined,
                        test_case_name + '.py')

    with open(path) as f:
        content = f.readlines()
    
    #execute_script_content = get_execute_script_content(content)

    description = get_description(content)

    page_objects = get_page_objects(content)

    #datos = get_datos(content)

    steps = _get_steps(content)

    test_case = {
        'description': description,
        'page_objects': page_objects,
        #'datos': datos,
        'steps': steps,
    }

    return test_case


def new_test_case(root_path, project, parents, tc_name):
    parents_joined = os.sep.join(parents)

    test_case_path = os.path.join(
        root_path, 'projects', project, 'test_cases', parents_joined)
    if not os.path.exists(test_case_path):
        os.makedirs(test_case_path)
    test_case_full_path = os.path.join(test_case_path, tc_name + '.py')

    data_path = os.path.join(root_path,
                             'projects',
                             project,
                             'data',
                             parents_joined)
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    data_full_path = os.path.join(data_path, tc_name + '.csv')

    with open(test_case_full_path, 'w') as f:
        f.write(test_case_content.format(tc_name))

    with open(data_full_path, 'w') as f:
        f.write('')


test_case_content = """from golem.core.actions import *
from golem.core import execution_logger as logger

# page objects


class {0}:    

    description = ''''''
    
    def setup(self):
        logger.description = self.description

    def test(self, data):
        pass

    def teardown(self):
        close()
"""


def format_parameters(parameters, root_path, project, parents, test_case_name):
    all_parameters = []
    for parameter in parameters:
        if page_object.is_page_object(parameter, root_path, project):
            # it is a page object, leave as is
            this_parameter_string = parameter
        else:
            # is not a page object,
            # identify if its a value or element parameter
            if data.is_data_variable(root_path,
                                     project,
                                     parents,
                                     test_case_name,
                                     parameter):
                this_parameter_string = 'data[\'{}\']'.format(parameter)
            else:
                this_parameter_string = '\'' + parameter + '\''
        all_parameters.append(this_parameter_string)

    all_parameters_string = ', '.join(all_parameters)
    return all_parameters_string


def format_page_object_import_string(project, page_object):
    po, parents = utils.separate_file_from_parents(page_object)
    if parents:
        parents = '.' + '.'.join(parents)
    else:
        parents = ''
    po_import_string = 'from projects.{0}.pages{1} ' \
                       'import {2}\n'.format(project, parents, po)
    return po_import_string


def save_test_case(root_path, project, full_test_case_name, description, 
                   page_objects, test_steps):
    tc_name, parents = utils.separate_file_from_parents(full_test_case_name)
    test_case_path = os.path.join(root_path,
                                  'projects',
                                  project,
                                  'test_cases', 
                                  os.sep.join(parents),
                                  '{}.py'.format(tc_name))

    with open(test_case_path, 'w') as f:

        f.write('from golem.core.actions import *\n')
        f.write('from golem.core import execution_logger as logger\n')
        f.write('\n')
        f.write('# page objects\n')
        for po in page_objects:
            f.write(format_page_object_import_string(project, po))
        f.write('\n')
        f.write('\n')
        f.write('class {}:\n'.format(tc_name))
        f.write('\n')
        f.write('    description = \'\'\'{}\'\'\'\n'.format(description))
        f.write('\n')
        f.write('    def setup(self):\n')
        f.write('        logger.description = self.description\n')
        f.write('\n')
        f.write('    def test(self, data):\n')
        if test_steps:
            for step in test_steps:
                f.write('        {0}({1})\n'.format(
                                                step['action'].replace(' ', '_'),
                                                format_parameters(
                                                    step['parameters'],
                                                    root_path,
                                                    project,
                                                    parents,
                                                    tc_name)))
        else:
            f.write('        pass\n')
        f.write('\n')
        f.write('    def teardown(self):\n')
        f.write('        close()\n')
