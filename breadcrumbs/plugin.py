"""
Defines the basic format of a plugin for the breadcrumbs system.
"""
from typing import Dict, Any

def load_plugin() -> Dict[str, Any]:
    """
    This is a function that will do what it need to to load the 'plugin' and
    return a string keyed dictionary that will be merged with all other plugins
    to form the final running config.

    :return: The configuration of the plugin.
    """

    # .. Do what you need to configure the plugin.
    # you may find the following keys usefull as they
    # have a predefined meaning.

    # This is where you put your plugin information
    plugin_data = {
        # who is responsible for this mess
        "author": "USER 1103",
        # Where can one find info about this plugin
        "website": "https://github.com/user-1103/breadcrumbs",
        # What version is the plugin
        "version": "0.1",
        # Description of the plugin
        "description": "An example plugin",
        # Specify any other plugins that should be loaded After
        "imports": [],
        # Put your internal runtime globals for your plugin here
        "lib": {},
        # Put your help topics here. Used by the help command.
        "help": {
            "usage": ("If you are reading this, you are already using this"
                      " plugin")
        }
    }

    # If you wish to rice your config look in here
    # there are four display profiles where you can 
    # provide you own custom methods to display the data,
    # so long as the function signature matches.
    display_settings = {
        # Used to debug the program
        "debug": {
            # Prints a crumb
            "crumb": "some_function(Task) -> None",
            # Prints a figure (non crumb data that is more complicated than
            # a single line of text)
            "figure": "some_function(Any) -> None",
            # Prints a single "toast" line of text
            "info": "some_function(Any) -> None",
            # Prints a single  warning "toast" line of text
            "warn": "some_function(Any) -> None",
            # Prints a error
            "err": "some_function(str, Exception) -> None",
            # Prints on exit
            "fatal": "some_function(str) -> None",
            # Clear the display
            "clear": "some_function() -> None",
            # print the title of the "screen" that is being used
            "title": "some_function(str) -> None",
            # print the title of the "screen" that is being used
            "prompt": "some_function(str) -> str"
        },
        # Used under normal conditions
        "normal": {}, #Expects the same set as debug
        # Used to comunicate to other programs
        "json": {}, #Expects the same set as debug
        # Used in reduced text environment
        "simple": {}, #Expects the same set as debug
        }

    # Hooks can be used to run functions when a given event happens
    # Hooks will be passed the final config dictionary and should
    # return None
    hooks = {
        # Called  after final config is loaded
        "INIT": ["some_function(Dict[str,Any], TodoTxt) -> bool"],
        # Called before macro expantion
        "PREMACRO": [],
        # Called before running the command
        "PRECMD": [],
        # Called on cmd err
        "CMDERR": [],
        # Called on cmd successful
        "CMDOK": [],
        # Called after command execution regardless
        "POSTCMD": [],
        # Called on exit regardless
        "EXIT": [],
        # Called on clean exit
        "SAFEEXIT": [],
        # Called on unclean exit
        "FATALEXIT": [],
        # Called before printing crumbs
        "PRINTCRUMB": [],
        # Called before printing figures
        "PRINTFIGURE": [],
        # Called before printing figures
        "PRINTFIGURE": [],
    }

    # This is the set of register commands that the user can invoke.
    # The keys are the names of the commands. Th user will have to 
    # type these so keep it simple and don't fuck up the 'synergy' of
    # the other commands. The values are functions that will be called
    # with the final config, loaf, and a string representing the args
    # after the command. The function should return a bool indicating if
    # the loaf should be saved after the command.
    commands = {
        # This would not be a good name for a command
        "exammple_cmd": "some_function(Dict[str,Any], TodoTxt, str) -> bool"
    }

    # These are the live buffers that are used for the basic
    # functions of the system. You can read and write to them.
    # Here be dragons!
    buffers = {
        # The TodoTxt object used to manage the loaf
        'loaf': 'TodoTxt',
        # A collection of selected Task objects
        'selection_buffer': 'List[Task]',
        # The expiration date of the data in the selection_buffer
        'selection_buffer_exp': 'float',
        # The raw of the last user input, no processesing
        'input_raw': "some command",
        # The last user input, after macro expantion
        'input_post_macro': "some command expanded",
        # The name of the command that is about to be run.
        'cmd': "some command expanded",
        # The args of the command that is about to be run.
        'args': "some command expanded",
        # The last err thrown.
        'err': 'Exception'
    }

    # Each macro defined here will be expanded once before any command will be run
    # It is keyed by the name of the macro and the value is a tuple containing
    # the before and after regex
    macros = {
        # an example macro
        "macro_name": (r'before_regex', r'after_regex')
    }

    config = {
        # pick a unique name so it does not conflict with other plugins
        "example_plugin": plugin_data,
        # This is where the program expects program data to be
        "breadbox": 'Path("./path/to/the/breadbox")',
        # This is where one can fiddle with how things are displayed
        "display": display_settings,
        # Hooks are attached here
        "hooks": hooks,
        # This is where the commands get defined.
        'commands': commands,
        # This is the default command that is run if none that maches is found
        'default_command': "some_function(Dict[str,Any], TodoTxt, str) -> bool",
        # This is called if the user provides aruments but no command
        'null_command': "some_function(Dict[str,Any], TodoTxt, str) -> bool",
        # This will be used as the default date if one cant be found
        'default_date': '1989-04-15',
        # This will be used as the default time if one cant be found
        'default_time': '06-28',
        # This will be used as the default span if one cant be found
        'default_span': '1d-~',
        # This will be used as the default sequence if one cant be found
        'default_sequence': 'n-1d',
        # This is where global working buffers are kept, edit with care!
        'buffers': buffers,
        # This is your preferred external editor command. %P will be replaced with path.
        'editor': "vim %P",
        # This will be set to the display profile that will be used
        'log': display_settings["normal"],
        # macros are set here
        'macros': macros
    }

    return config




