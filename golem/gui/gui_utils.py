import csv
import datetime
import os


# def go_one_level_deeper__DEPRECADO(file_structure, this_dir_file_structure, current_directory, parents):
#     first_parent = parents[0]
#     parents.pop(0)
#     if len(parents) == 0:

#         file_structure['childirs'][current_directory] = this_dir_file_structure
#     else: 
#         file_structure['childirs'][first_parent] = go_one_level_deeper(
#                                     file_structure['childirs'][first_parent],
#                                     this_dir_file_structure,
#                                     current_directory,
#                                     parents)
#     return file_structure


# def get_test_cases__DEPRECADO(workspace, project):
#     path = os.path.join(workspace, 'projects', project, 'test_cases')

#     file_structure = {
#         'name': '',
#         'files': [],
#         'childirs': {} }

#     for root, dirs, files in os.walk(path):
#         parents = root.replace(path, '').split(os.sep)
#         parents.pop(0)
#         current_directory = os.path.basename(root)
#         files = [x[:-3] for x in files]
#         if '__init__' in files: files.remove('__init__')
#         this_dir_file_structure = {
#                                     'name': current_directory,
#                                     'files': files,
#                                     'childirs': {} }
#         if len(parents) == 0:
#             file_structure = this_dir_file_structure
#         else:
#             file_structure = go_one_level_deeper(
#                                         file_structure, 
#                                         this_dir_file_structure, 
#                                         current_directory,
#                                         parents)

#     return file_structure

def get_page_objects_DEPRECADO(workspace, project):
    # find page objects directory

    page_objects_directory = ''
    #page_objects = []

    path = os.path.join(workspace, 'projects', project, 'pages')

    file_structure = {
        'name': '',
        'files': [],
        'childirs': {} }
        
    for root, dirs, files in os.walk(path):
        parents = root.replace(path, '').split(os.sep)
        parents.pop(0)
        current_directory = os.path.basename(root)
        files = [x[:-3] for x in files]
        if '__init__' in files: files.remove('__init__')

        this_dir_file_structure = {
                    'name': current_directory,
                    'files': files,
                    'childirs': {} }

        if len(parents) == 0:
            file_structure = this_dir_file_structure
        else:
            file_structure = go_one_level_deeper(
                                        file_structure, 
                                        this_dir_file_structure, 
                                        current_directory,
                                        parents)

    return file_structure



def new_directory(root_path, project, parents, directory_name):
    parents_joined = os.sep.join(parents)

    directory_path = os.path.join(
        root_path, 'projects', project, 'test_cases', parents_joined, directory_name)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def new_directory_page_object(root_path, project, parents, directory_name):
    parents_joined = os.sep.join(parents)

    directory_path = os.path.join(
        root_path, 'projects', project, 'pages', parents_joined, directory_name)

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    # add __init__.py file to make the new directory a python package
    init_path = os.path.join(directory_path, '__init__.py')
    open(init_path, 'a').close()


def run_test_case(project, test_case_name):
    os.system('python golem.py run {0} {1}'.format(project, test_case_name))


def get_time_span(task_id):

    path = os.path.join('results', '{0}.csv'.format(task_id))
    if not os.path.isfile(path):
        log_to_file('an error')
        return
    else: 
        with open(path, 'r') as f:
            reader = csv.DictReader(f, delimiter=';') 
            last_row = list(reader)[-1]
            exec_time = string_to_time(last_row['time'])
            time_delta = datetime.datetime.now() - exec_time
            total_seconds = time_delta.total_seconds()
            return total_seconds


def directory_already_exists(root_path, project, root_dir, parents, dir_name):
    parents_joined = os.sep.join(parents)

    directory_path = os.path.join(
        root_path, 'projects', project, root_dir, parents_joined, dir_name)    

    if os.path.exists(directory_path):
        return True
    else:
        return False


def file_already_exists(root_path, project, root_dir, parents, filename):
    parents_joined = os.sep.join(parents)

    directory_path = os.path.join(
        root_path, 'projects', project, root_dir, parents_joined, filename + '.py')    

    if os.path.isfile(directory_path):
        return True
    else:
        return False


def log_to_file(string):
    print string


def time_to_string():
    time_format = '%Y-%m-%d-%H-%M-%S-%f'
    return datetime.datetime.now().strftime(time_format)


def string_to_time(time_string):
    return datetime.datetime.strptime(time_string, '%Y-%m-%d-%H-%M-%S-%f')


def get_global_actions():
    global_actions = [
        {
            'name': 'click',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'send keys',
            'parameters': [{'name': 'element', 'type': 'element'},
                           {'name': 'value', 'type': 'value'}]
        },
        {
            'name': 'select',
            'parameters': [{'name': 'option', 'type': 'value'},
                           {'name': 'from element', 'type': 'element'}]
        },
        {
            'name': 'go to',
            'parameters': [{'name': 'url', 'type': 'value'}]
        },
        {
            'name': 'verify text',
            'parameters': [{'name': 'text', 'type': 'value'}]
        },
        {
            'name': 'verify text in element',
            'parameters': [{'name': 'text', 'type': 'value'},
                           {'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify exists',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify not exists',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify is enabled',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'verify is not enabled',
            'parameters': [{'name': 'element', 'type': 'element'}]
        },
        {
            'name': 'screenshot',
            'parameters': [{'name': 'message (optional)', 'type': 'value'}]
        },
    ]
    return global_actions