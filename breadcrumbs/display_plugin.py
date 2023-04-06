"""
This plugin consists of establishing the most basic display capabilities.
"""

from enum import Enum, auto
from json import dumps
from typing import Dict, Any, Union
from pytodotxt import Task, TodoTxt
from rich.align import Align

from rich.panel import Panel
from rich.table import Table


from breadcrumbs.lexer import TodotxtLexer
from rich.syntax import Syntax
from rich.console import Console, RenderableType

# The lexer to use for crumbs
lex = TodotxtLexer()
# The rich console to use
console = Console()
# Is a json list being printed
is_json_list = False

def easy_lex(text: Any) -> Syntax:
    """
    Wrap text in a syntax block.

    :param text: the text to wrap.
    :return: the wrapped object.
    """
    tmp = Syntax(str(text), lexer=lex, word_wrap = True,
                               theme="ansi_light")
    return tmp

def log(text: Any) -> None:
    """
    Logs a renderable in a debugy way.

    :param text: The object to log.
    """
    console.log(text, markup=True)

class LogType(Enum):
    CRUMB = auto()
    FIGURE = auto()
    INFO = auto()
    WARN = auto()
    DEBUG = auto()
    CLEAR = auto()
    TITLE = auto()
    ERR = auto()
    FATAL = auto()

def debug_log(text: Any = "Default Text", err: Union[Exception, None] = None,
               ltype: LogType = LogType.INFO) -> None:
    """
    Logs a renderable in a debugy way.

    :param text: The object to log.
    :param err: If present, an err to log.
    :param ltype: The type of the object being logged.
    """
    if (ltype == LogType.CRUMB):
        log("<CRUMB>")
        tmp = easy_lex(text)
        log(tmp)
    elif (ltype == LogType.FIGURE):
        log("<FIGURE>")
        log(text)
    elif (ltype == LogType.INFO):
        log("<INFO>")
        log(text)
    elif (ltype == LogType.WARN):
        log("<WARN>")
        log(text)
    elif (ltype == LogType.DEBUG):
        log("<DEBUG>")
        log(text)
    elif (ltype == LogType.CLEAR):
        log("<CLEAR>")
    elif (ltype == LogType.TITLE):
        log("<TITLE>")
        log(text)
    elif (ltype == LogType.ERR):
        log("<ERR>")
        log(text)
        console.print_exception()
    elif (ltype == LogType.FATAL):
        log("<FATAL>")
        log(text)

def normal_log(text: Any = "Default Text", err: Union[Exception, None] = None,
               ltype: LogType = LogType.INFO) -> None:
    """
    Logs a renderable in a pretty way.

    :param text: The object to log.
    :param err: If present, an err to log.
    :param ltype: The type of the object being logged.
    """
    if (ltype == LogType.CRUMB):
        tmp = easy_lex(text.description)
        tmp_panel = Panel(tmp)
        console.print(tmp_panel)
    elif (ltype == LogType.FIGURE):
        tmp = Align(text, align="center", vertical="middle")
        tmp_panel = Panel(tmp, border_style="blue", safe_box=False)
        console.print(tmp_panel)
    elif (ltype == LogType.INFO):
        tmp = f"  🡢  {text}"
        console.print(tmp)
    elif (ltype == LogType.WARN):
        tmp = f"  🡢  {text}"
        console.print(tmp, style="yellow")
    elif (ltype == LogType.DEBUG):
        ...
    elif (ltype == LogType.CLEAR):
        console.clear()
    elif (ltype == LogType.TITLE):
        console.rule(text)
    elif (ltype == LogType.ERR):
        tmp = f"  🡢  {text} (ERROR) 🡢  {type(err)}: {err}"
        console.print(tmp, style="red")
        console.print_exception()
    elif (ltype == LogType.FATAL):
        tmp = f"  🡢  {text} (EXIT)"
        console.print(tmp, style="red")

def json_log(text: Any = "Default Text", err: Union[Exception, None] = None,
               ltype: LogType = LogType.INFO) -> None:
    """
    Logs a renderable in a json way.

    :param text: The object to log.
    :param err: If present, an err to log.
    :param ltype: The type of the object being logged.
    """
    global is_json_list
    if (not is_json_list):
        print("[")
        is_json_list = True
    if (ltype == LogType.CRUMB):
        tmp = {
            "_type": "crumb",
            "data": str(text)
        }
        tmp_json = dumps(tmp)
        print(tmp_json + ",")
    elif (ltype == LogType.FIGURE):
        tmp = {
            "_type": "figure",
            "data": str(text)
        }
        tmp_json = dumps(tmp)
        print(tmp_json + ",")
    elif (ltype == LogType.INFO):
        tmp = {
            "_type": "info",
            "data": str(text)
        }
        tmp_json = dumps(tmp)
        print(tmp_json + ",")
    elif (ltype == LogType.WARN):
        tmp = {
            "_type": "warn",
            "data": str(text)
        }
        tmp_json = dumps(tmp)
        print(tmp_json + ",")
    elif (ltype == LogType.DEBUG):
        tmp = {
            "_type": "debug",
            "data": str(text)
        }
        tmp_json = dumps(tmp)
        print(tmp_json + ",")
    elif (ltype == LogType.CLEAR):
        tmp = {
            "_type": "clear"
        }
        tmp_json = dumps(tmp)
        print(tmp_json + ",")
    elif (ltype == LogType.TITLE):
        tmp = {
            "_type": "title",
            "data": str(text)
        }
        tmp_json = dumps(tmp)
        print(tmp_json + ",")
    elif (ltype == LogType.ERR):
        tmp = {
            "_type": "err",
            "data": str(text)
        }
        tmp_json = dumps(tmp)
        print(tmp_json + ",")
    elif (ltype == LogType.FATAL):
        tmp = {
            "_type": "fatal",
            "data": str(text)
        }
        tmp_json = dumps(tmp)
        print(tmp_json)
        is_json_list = False
        print("]")

def simple_log(text: Any = "Default Text", err: Union[Exception, None] = None,
               ltype: LogType = LogType.INFO) -> None:
    """
    Logs a renderable in a simple way.

    :param text: The object to log.
    :param err: If present, an err to log.
    :param ltype: The type of the object being logged.
    """
    if (ltype == LogType.CRUMB):
        print("<CRUMB>")
        tmp = text
        print(tmp)
    elif (ltype == LogType.FIGURE):
        print("<FIGURE>")
        print(text)
    elif (ltype == LogType.INFO):
        print("<INFO>")
        print(text)
    elif (ltype == LogType.WARN):
        print("<WARN>")
        print(text)
    elif (ltype == LogType.DEBUG):
        print("<DEBUG>")
        print(text)
    elif (ltype == LogType.CLEAR):
        print("<CLEAR>")
    elif (ltype == LogType.TITLE):
        print("<TITLE>")
        print(text)
    elif (ltype == LogType.ERR):
        print("<ERR>")
        print(text)
        print(err)
    elif (ltype == LogType.FATAL):
        print("<FATAL>")
        print(text)

def prompt(text: str = "") -> str:
    """
    Prompts the user for input.

    :param text: A question for the user.
    :return: The user input.
    """
    text = f" {text} 🡠  "
    ret = input(text)
    return ret

def display_test_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Runs through all renderables Used for debuging.
    - Does not save under any condition.
    """
    t = Table(title="Test Figure")
    t.add_column("Bread Type", "Rating")
    t.add_row("Wonder", "0/10")
    t.add_row("Ezekiel", "5/10")
    t.add_row("Garlic", "10/10")
    for name, profile in conf["display"].items():
        profile["clear"]()
        profile["title"]("DISPLAY TEST")
        profile["crumb"](Task("(A) 1971-01-01 Example Crumb +test @debug tag:true"))
        profile["crumb"](Task("x (A) 1971-01-01 Example Crumb +test @debug tag:true"))
        profile["figure"](t)
        profile["info"]("Putting bread in oven...")
        profile["debug"]("Oven at 1000 degrees C.")
        profile["warn"]("Oven is smoking...")
        try:
            raise Exception("lp0 on fire")
        except Exception as e:
            profile["err"]("Oven is on fire...", e)
        profile["fatal"]("Run.")
        profile["prompt"]("Enter some text to continue.")
    return False


def load_plugin() -> Dict[str, Any]:
    """
    This is a function that will do what it need to to load the 'plugin' and
    return a string keyed dictionary that will be merged with all other plugins
    to form the final running config.

    :return: The configuration of the plugin.
    """
    plugin_data = {
        "author": "USER 1103",
        "website": "https://github.com/user-1103/breadcrumbs",
        "version": "0.1",
        "description": "Sets the default display capabilities.",
        "imports": [],
        "lib": {
            'easy_lex': easy_lex
        },
        "help": {
            "usage": ("If you are reading this, you are already using this"
                      " plugin")
        }
    }

    display_settings = {
        "debug": {
            "crumb": lambda x: debug_log(x, ltype=LogType.CRUMB),
            "figure": lambda x: debug_log(x, ltype=LogType.FIGURE),
            "info": lambda x: debug_log(x, ltype=LogType.INFO),
            "debug": lambda x: debug_log(x, ltype=LogType.DEBUG),
            "warn": lambda x: debug_log(x, ltype=LogType.WARN),
            "err": lambda x, y: debug_log(x, y, ltype=LogType.ERR),
            "fatal": lambda x: debug_log(x, ltype=LogType.FATAL),
            "clear": lambda : debug_log(ltype=LogType.CLEAR),
            "title": lambda x: debug_log(x, ltype=LogType.TITLE),
            "prompt": prompt
        },
        "normal": {
            "crumb": lambda x: normal_log(x, ltype=LogType.CRUMB),
            "figure": lambda x: normal_log(x, ltype=LogType.FIGURE),
            "info": lambda x: normal_log(x, ltype=LogType.INFO),
            "debug": lambda x: normal_log(x, ltype=LogType.DEBUG),
            "warn": lambda x: normal_log(x, ltype=LogType.WARN),
            "err": lambda x, y: normal_log(x, y, ltype=LogType.ERR),
            "fatal": lambda x: normal_log(x, ltype=LogType.FATAL),
            "clear": lambda : normal_log(ltype=LogType.CLEAR),
            "title": lambda x: normal_log(x, ltype=LogType.TITLE),
            "prompt": prompt
        },
        "json": {
            "crumb": lambda x: json_log(x, ltype=LogType.CRUMB),
            "figure": lambda x: json_log(x, ltype=LogType.FIGURE),
            "info": lambda x: json_log(x, ltype=LogType.INFO),
            "debug": lambda x: json_log(x, ltype=LogType.DEBUG),
            "warn": lambda x: json_log(x, ltype=LogType.WARN),
            "err": lambda x, y: json_log(x, y, ltype=LogType.ERR),
            "fatal": lambda x: json_log(x, ltype=LogType.FATAL),
            "clear": lambda : json_log(ltype=LogType.CLEAR),
            "title": lambda x: json_log(x, ltype=LogType.TITLE),
            "prompt": prompt
        },
        "simple": {
            "crumb": lambda x: simple_log(x, ltype=LogType.CRUMB),
            "figure": lambda x: simple_log(x, ltype=LogType.FIGURE),
            "info": lambda x: simple_log(x, ltype=LogType.INFO),
            "debug": lambda x: simple_log(x, ltype=LogType.DEBUG),
            "warn": lambda x: simple_log(x, ltype=LogType.WARN),
            "err": lambda x, y: simple_log(x, y, ltype=LogType.ERR),
            "fatal": lambda x: simple_log(x, ltype=LogType.FATAL),
            "clear": lambda : simple_log(ltype=LogType.CLEAR),
            "title": lambda x: simple_log(x, ltype=LogType.TITLE),
            "prompt": lambda x: input(f" {x} > ")
        },
        }

    commands = {
        "display-test": display_test_cmd
    }

    config = {
        'plugins': {"display": plugin_data},
        "display": display_settings,
        'commands': commands,
        'log': display_settings["normal"]
    }

    return config
