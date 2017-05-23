import argparse


def get_golem_parser():
    '''parser of comand line arguments for golem (main program)'''

    parser = argparse.ArgumentParser(
                    description='run test case, test suite or start the Golem GUI tool',
                    usage='golem run project_name test_case|test_suite',
                    add_help=False)

    sub_parsers = parser.add_subparsers(dest="main_action")

    # run
    run_parser = sub_parsers.add_parser('run')
    run_parser.add_argument('project', default='', nargs='?', help="project name")
    run_parser.add_argument('test_or_suite', nargs='?', default='', metavar='test case or suite',
                            help="test case or test suite to run")
    run_parser.add_argument('-t', '--threads', action='store', nargs='?', default=1, type=int,
                            metavar='amount of threads for parallel execution',
                            help="amount of threads for parallel execution")
    run_parser.add_argument('-d', '--drivers', action='store', nargs='*', 
                            choices=['firefox', 'chrome'], type=str, metavar='Web Drivers',
                            help="Web Drivers")
    run_parser.add_argument('--timestamp', action='store', nargs='?', type=str,
                            metavar='Timestamp', help="Timestamp")

    # gui
    gui_parser = sub_parsers.add_parser('gui')
    gui_parser.add_argument('-p', '--port', action='store', nargs='?', default=5000, type=int,
                            metavar='port number', help="port number to use for Golem GUI")
    gui_parser.add_argument('-d', '--debug', action='store_true', default=False,
                            help="Start the gui application in debug mode")

    # createproject
    create_project_parser = sub_parsers.add_parser('createproject')
    create_project_parser.add_argument('project', help="project name")

    # createtest
    create_test_parser = sub_parsers.add_parser('createtest')
    create_test_parser.add_argument('project', help="project name")
    create_test_parser.add_argument('test', metavar='test case name', help="test case name")

    #createsuite
    create_suite_parser = sub_parsers.add_parser('createsuite')
    create_suite_parser.add_argument('project', help="project name")
    create_suite_parser.add_argument('suite', metavar='suite name', help="suite name")

    # createuser
    createuser_parser = sub_parsers.add_parser('createuser')
    createuser_parser.add_argument('username', help="username")
    createuser_parser.add_argument('password', help="suite name")
    createuser_parser.add_argument('-a', '--admin', action='store_true', default=False,
                                   help="is admin")
    createuser_parser.add_argument('-p', '--projects', nargs='+', default=[],
                                   help="projects the user has access")
    createuser_parser.add_argument('-r', '--reports', nargs='+', default=[],
                                   help="reports the user has access")
    return parser


def get_golem_admin_parser():
    '''parser of comand line arguments for golem-admin script'''

    parser = argparse.ArgumentParser(add_help=False)

    sub_parsers = parser.add_subparsers(dest="main_action")

    new_directory_parser = sub_parsers.add_parser('createdirectory')
    new_directory_parser.add_argument('name', metavar='name', help="directory name")

    return parser
