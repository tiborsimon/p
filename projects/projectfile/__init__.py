from . import data_processor
from . import file_handler
import os

DEFAULT_PROJECTFILE = '''\
from v{}

"""
This is a template Projectfile you have created with the 'p [-i|--init]' command.
You can use the provided commands 'hello' and 'answer' or it's shorter alternatives
'h' and 'ans' or 'a'. ie.: p <command>

You can start a new paragraph in the descriptions by inserting an empty line like this.

Descriptions are useful as they provide a searchable manual for your project for free.
"""

magic = 42

hello|h: [a]
    """
    This command will great you.

    There is a shorter alternative "h" for the command. It is also depending on the
    "a" command which is the alternative of the "answer" command.

    If you execute a dependent command, it's dependencies will be executed first
    in order.
    """
    echo "This is the my very own Projectfile."

answer|ans|a:
    """
    This command will give you the answer for every question.

    You can use the long "answer" keyword as well as the shorter "ans" or "a" to
    execute this command.

    Inside the Projectfile, you can also refer to a command in another command's
    dependency list by any of it's alternatives.
    """
    echo "The answer for everything is $magic!"
'''


def get_data_for_root(project_root):
    """This is the only API function of the projectfile module. It parses the Projectfiles
    from the given path and assembles the flattened command data structure.

    Returned data: {
        'min-version': (1, 0, 0),
        'description': 'Optional main description.',
        'commands': {
            'command_1': {
                'description': 'Optional command level description for command_1.',
                'script': [
                    'flattened',
                    'out command',
                    'list for',
                    'command_1',
                    ...
                ]
            }
            ...
        }
    }

    Raises:
        ProjectfileError with descriptive error message in the format of:
        {
            'path': 'Optional path for the corresponding Projectfile.',
            'line': 'Optional line number for the error in the Projectfile.',
            'error': 'Mandatory descriptive error message.'
        }


    :param project_root:
    :return: {dict} parsed and flattened commands with descriptions
    """
    processing_tree = data_processor.generate_processing_tree(project_root)
    data = data_processor.finalize_data(processing_tree)
    data_processor.process_variables(data)
    return data


def get_walk_order(project_root):
    starting = ['.git', '.svn', 'node_modules']
    ending = ['__pycache__']
    data = file_handler.get_walk_data(project_root)
    print('')
    for root, dirs, files in data:
        root = root[len(project_root) + 1:]
        for e in starting:
            if root.startswith(e):
                break
        else:
            for e in ending:
                if root.endswith(e):
                    break
            else:
                if not root:
                    root = '.'
                if os.path.isfile(os.path.join(root, 'Projectfile')):
                    print(' [x] ' + root)
                else:
                    print(' [ ] ' + root)

