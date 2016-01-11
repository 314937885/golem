import os, re

from golem.gui import data, page_object

from golem.gui import gui_utils

def get_steps(content):

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
            if len(current_line.strip()) > 0:
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
    if index >= 0:
        page_object_line = content[index]
        if 'import' in page_object_line:
            page_objects = page_object_line.split('import')[1].split(',')
            page_objects = [x.strip() for x in page_objects]
    return page_objects


def get_description(content):

    contentString = ''.join(content)
    description = ''
    index = 0
    description = re.search(".*description = \'\'\'(.*\n*.*)\'\'\'", contentString).group(1)
    description = re.sub("\s\s+", " ", description)
    # for i, line in enumerate(content): 
    #     # if 'description' in line:
    #     #     index = i
    #     if re.match("(.*)description(.*)", line):
    #         print line
    #         print re.search("\'\'\'(.*)\'\'\'", line).group(1)
    # if index != 0:
    #     description += content[index].split('\'\'\'')[1]
    #     keep_reading = False
    #     print content[index][-3:-1]
    #     if content[index][-3:-1] != '\'\'\'':
    #         keep_reading = True
    #     while keep_reading:
    #         index += 1
    #         description += content[index].split('\'\'\'')[0]
    #         if content[index][-3:-1] == '\'\'\'':
    #             keep_reading = False
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
        workspace, 'projects', project, 'test_cases', parents_joined, test_case_name + '.py')

    with open(path) as f:
        content = f.readlines()
    
    #execute_script_content = get_execute_script_content(content)

    description = get_description(content)

    page_objects = get_page_objects(content)

    #datos = get_datos(content)

    steps = get_steps(content)

    test_case = {
        'description': description,
        'page_objects': page_objects,
        #'datos': datos,
        'steps': steps,
    }

    return test_case


def new_test_case(root_path, project, tc_name):
    test_case_path = os.path.join(
        root_path, 'projects', project, 'test_cases', tc_name + '.py')

    data_path = os.path.join(
        root_path, 'projects', project, 'data', tc_name + '.py')

    with open(test_case_path, 'w') as f:
        f.write(test_case_content)

    with open(data_path, 'w') as f:
        f.write('')


test_case_content = """from golem.core.test import Test
from golem.core.actions import *
from golem.core import execution_logger as logger
# page objects

class search_article:    

    description = ''''''
    
    def setup(self):
        logger.description = self.description
        pass

    def test(self):
            
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
            if data.is_data_variable(root_path, project, parents, test_case_name, parameter):
                this_parameter_string = 'data[\'{}\']'.format(parameter)
            else:
                this_parameter_string = '\'' + parameter + '\''
        all_parameters.append(this_parameter_string)

    all_parameters_string = ','.join(all_parameters)
    return all_parameters_string


def save_test_case(root_path, project, test_case_name, description, page_objects, test_steps):
    test_case_path = os.path.join(
        root_path, 'projects', project, 'test_cases', test_case_name + '.py')

    with open(test_case_path, 'w') as f:

        f.write('from golem.core.test import Test\n')
        f.write('from golem.core.actions import *\n')
        f.write('from golem.core import execution_logger as logger\n')
        f.write('# page objects\n')
        f.write('from projects.'+project+'.pages import '+', '.join(page_objects) +'\n')
        f.write('\n')
        f.write('class {}:\n'.format(test_case_name))
        f.write('\n')
        f.write('    description = \'\'\'{}\'\'\'\n'.format(description))
        f.write('\n')
        f.write('    def setup(self):\n')
        f.write('        logger.description = self.description\n')
        f.write('        pass\n')
        f.write('\n')
        f.write('    def test(self, data):\n')
        for step in test_steps:
            f.write('        {0}({1})\n'.format(
                                            step['action'].replace(' ', '_'),
                                            format_parameters(
                                                step['parameters'],
                                                root_path,
                                                project,
                                                [],
                                                test_case_name)))
        f.write('\n')
        f.write('    def teardown(self):\n')
        f.write('        close()\n')