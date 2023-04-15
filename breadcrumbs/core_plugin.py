"""
Defines the core commands in a plugin.
"""
from datetime import datetime
from json import loads
from re import sub
from subprocess import run
from typing import Dict, Any
from deep_translator.base import Path

from pytodotxt import Task, TodoTxt
from tempfile import NamedTemporaryFile, TemporaryFile
from rich.table import Table
from breadcrumbs.utils import add_task, archive, drop_buffer, easy_lex, get_contexts, get_projects, get_tags, loaf_search, unarchive, get_buffer, set_buffer


def print_buffer_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Prints the contents of the selected buffer.
    - Does not save under any condition.
    """
    res = get_buffer(conf)
    buffer_time = conf["buffers"]["selection_buffer_exp"]
    exp_time = datetime.fromtimestamp(buffer_time)
    conf["log"]["clear"]()
    conf["log"]["title"]("SELECTION BUFFER")
    for x in res:
        conf["log"]["crumb"](x)
    if (not res):
        conf["log"]["info"]("Buffer is empty...")
    else:
        conf["log"]["info"](f"Buffer auto-expires at {exp_time}.")
    return False

def raw_add_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <crumb> -> The crumb to add.
    - Adds a crumb with no checking / modification.
    - Saves. Sets selection buffer.
    """
    tmp = Task(args)
    loaf.add(tmp)
    res = loaf_search(loaf, span="1d-~", archived=False)
    conf["log"]["clear"]()
    conf["log"]["title"]("BREADCRUMB TRAIL")
    for x in res:
        conf["log"]["crumb"](x)
    set_buffer(conf, [tmp])
    return True

def add_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <crumb> -> The crumb to add.
    - Adds a crumb.
    - Saves. Sets selection buffer.
    """
    tmp = add_task(loaf, args)
    if (not tmp.description):
        return False
    res = loaf_search(loaf, span="1d-~", archived=False)
    conf["log"]["clear"]()
    conf["log"]["title"]("BREADCRUMB TRAIL")
    for x in res:
        conf["log"]["crumb"](x)
    set_buffer(conf, [tmp])
    return True

def export_json_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <path_to_save_to> -> The path to save too.
    - Exports a the selection buffer as json.
    - Does Not Save.
    """
    ...

def edit_external_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <editor_command> -> Optional. If present the editor_command will be
      executed with the %P replaced with the path to the current selection
      buffer on disk. Otherwise the editor config is used.
    - Opens an external editor to edit the selection buffer.
    - Saves. Sets selection buffer.
    """
    if (args):
        edit = args
    else:
        edit = conf['editor']
    tmp = edit.replace("%P", (conf['breadbox'] + "/selection_buffer"))
    try:
        ret = run(tmp, shell= True, encoding='utf-8', check=True)
    except Exception as e:
        conf['log']['err']("Not saving...", e)
        return False
    else:
        drop_buffer(conf)
        t = TodoTxt(Path(conf['breadbox'] + '/selection_buffer'))
        res = t.parse()
        for x in res:
            loaf.add(x)
        set_buffer(conf, res)
        print_buffer_cmd(conf, loaf, "")
    return True

def block_add_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <prepend_str>/<append_str>
      - <prepend_str> -> The string to prepend all crumbs in the block with.
      - <append_str> -> The string to append all crumbs in the block with.
    - Adds a crumb.
    - Saves. Sets selection buffer.
    """
    try:
        prefix_str, postfix_str = args.split("/")
    except Exception as e:
        prefix_str = ""
        postfix_str = args
    conf["log"]["clear"]()
    t = Table(title="Editing in block mode using:",
              caption="(Type END to finish block edit)")
    t.add_column("Prefix")
    t.add_column("Postfix")
    t.add_row(easy_lex(prefix_str), easy_lex(postfix_str))
    conf["log"]["title"]("BLOCK EDIT")
    conf["log"]["figure"](t)
    add_text = ""
    tmp = list()
    while (True):
        add_text = conf["log"]["prompt"]()
        if (add_text == "END"):
            break
        tmp.append(add_task(loaf, f"{prefix_str} {add_text} {postfix_str}"))
        conf["log"]["clear"]()
        conf["log"]["title"]("BLOCK EDIT")
        conf["log"]["figure"](t)
        for x in tmp:
            conf["log"]["crumb"](x)
    conf["log"]["clear"]()
    conf["log"]["title"]("BLOCK EDIT")
    conf["log"]["figure"](t)
    for x in tmp:
        conf["log"]["crumb"](x)
    conf["log"]["info"]("Saving Block")
    set_buffer(conf, tmp)
    return True

def nop_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Nothing.
    - Never saves.
    """
    conf["log"]["info"]("Use ?ic to list commands")
    return True

def projects_info_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Prints all known projects.
    - Never saves.
    """
    conf["log"]["clear"]()
    conf["log"]["title"]("PROJECT INFO")
    t = Table(title="Known Projects.")
    t.add_column("Project Name")
    t.add_column("Count")
    res = get_projects(loaf)
    res_list = list(res.items())
    res_list.sort(key= lambda x: x[1])
    for k, v in res_list:
        t.add_row(f"{k}", f"{v}")
    conf["log"]["figure"](t)
    return False

def context_info_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Prints all known contexts.
    - Never saves.
    """
    conf["log"]["clear"]()
    conf["log"]["title"]("CONTEXTS INFO")
    t = Table(title="Known Contexts.")
    t.add_column("Context Name")
    t.add_column("Count")
    res = get_contexts(loaf)
    res_list = list(res.items())
    res_list.sort(key= lambda x: x[1])
    for k, v in res_list:
        t.add_row(f"{k}", f"{v}")
    conf["log"]["figure"](t)
    return False

def tag_info_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Prints all known tags.
    - Never saves.
    """
    conf["log"]["clear"]()
    conf["log"]["title"]("TAG INFO")
    t = Table(title="Known Tags.")
    t.add_column("Tag Name")
    t.add_column("Count")
    res = get_tags(loaf)
    res_list = list(res.items())
    res_list.sort(key= lambda x: x[1])
    for k, v in res_list:
        t.add_row(f"{k}", f"{v}")
    conf["log"]["figure"](t)
    return False

def command_info_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Prints all registered commands.
    - Never saves.
    """
    conf["log"]["clear"]()
    conf["log"]["title"]("COMMAND INFO")
    t = Table(title="Crumb Commands.")
    t.add_column("What You Type...")
    t.add_column("What Happens...")
    for k, v in conf["commands"].items():
        t.add_row(f"?{k}", v.__doc__)
    conf["log"]["figure"](t)
    return False

def macro_info_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Prints all registered macros.
    - Never saves.
    """
    # TODO add lexer for regex
    conf["log"]["clear"]()
    conf["log"]["title"]("MACRO INFO")
    t = Table(title="Macro Commands.")
    t.add_column("Name")
    t.add_column("Before Regex...")
    t.add_column("After Regex...")
    for k, v in conf["macros"].items():
        if (isinstance(v, tuple)):
            t.add_row(f"{k}", v[0], v[1])
        else:
            tmp = v.__doc__.splitlines()
            t.add_row(f"{k}", tmp[1], tmp[2])
    conf["log"]["figure"](t)
    return False

def hooks_info_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Prints all registered hooks.
    - Never saves.
    """
    conf["log"]["clear"]()
    conf["log"]["title"]("HOOK INFO")
    t = Table(title="Registered Hooks.")
    t.add_column("Hook")
    t.add_column("Registered Functions")
    for k, v in conf["hooks"].items():
        tmp = ""
        for x in v:
            tmp += f"{x.__name__}\n"
        t.add_row(k, tmp)
    conf["log"]["figure"](t)
    return False

def archive_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Archive all crumbs in selection buffer.
    - Always saves.
    """
    res = get_buffer(conf)
    archive(res)
    conf["log"]["clear"]()
    conf["log"]["title"]("ARCHIVED")
    for x in res:
        conf["log"]["crumb"](x)
    conf["log"]["info"](f"Archived {len(res)} crumbs.")
    return True

def unarchive_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Unarchive all crumbs in selection buffer.
    - Always saves.
    """
    res = get_buffer(conf)
    unarchive(res)
    conf["log"]["clear"]()
    conf["log"]["title"]("UNARCHIVED")
    for x in res:
        conf["log"]["crumb"](x)
    conf["log"]["info"](f"Unarchived {len(res)} crumbs.")
    return True

def select_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <search_str> -> A regex string to search with.
    - Uses regex to search / select the unarchived crumbs.
    - Saves. Sets selection buffer.
    """
    res = loaf_search(loaf, regex_str=args,
                      archived=False)
    set_buffer(conf, res)
    conf["log"]["clear"]()
    conf["log"]["title"]("SELECT")
    for x in res:
        conf["log"]["crumb"](x)
    return True

def select_archive_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <search_str> -> A regex string to search with.
    - Uses regex to search / select the archived crumbs.
    - Saves. Sets selection buffer.
    """
    res = loaf_search(loaf, regex_str=args,
                      archived=True)
    set_buffer(conf, res)
    conf["log"]["clear"]()
    conf["log"]["title"]("STALE SELECT")
    for x in res:
        conf["log"]["crumb"](x)
    return True

def sub_select_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Enters a mode to sub select crumbs in the selection buffer.
    - Does Not Save. Sets selection buffer.
    """
    res = get_buffer(conf)
    conf["log"]["clear"]()
    conf["log"]["title"]("SUB-SELECT MODE")
    t = Table(title="Selection Buffer.")
    t.add_column("ID")
    t.add_column("Crumb")
    for i, x in enumerate(res):
        t.add_row(str(i), easy_lex(x))
    conf["log"]["figure"](t)
    sel = conf["log"]["prompt"](f"Space Seperated ID Selection")
    sel_list = sel.split()
    tmp = list()
    for i, x in enumerate(res):
        if (str(i) in sel_list):
            tmp.append(x)
    set_buffer(conf, tmp)
    print_buffer_cmd(conf, loaf, args)
    return False

def advanced_select_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <search_json> -> Search json. See ?h core/search-json.
    - Uses search json to search / select crumbs.
    - Saves. Sets selection buffer.
    """
    search_json = loads(args)
    res = loaf_search(loaf, **search_json)
    set_buffer(conf, res)
    conf["log"]["clear"]()
    conf["log"]["title"]("ADVANCED SELECT")
    for x in res:
        conf["log"]["crumb"](x)
    return True

def list_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Prints the crumb trail for the last 24hr.
    - Never saves.
    """
    res = loaf_search(loaf, span="1d-~", archived=False)
    conf["log"]["clear"]()
    conf["log"]["title"]("BREADCRUMB TRAIL")
    for x in res:
        conf["log"]["crumb"](x)
    return False

def undo_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Undo the last addition.
    - Always saves.
    """
    tmp = loaf.tasks[-1]
    tmp.is_completed = True
    list_cmd(conf, loaf, args)
    conf["log"]["info"]("Undo successful...")
    return True

def substitute_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - <before_regex>/<after_regex>.
      - <before_regex> -> The regex to be replaced.
      - <after_regex> -> The regex to replace with.
    - Substitutes in a vi like way on all crumbs in buffer.
    - Always saves.
    """
    before_regex, after_regex = args.split("/")
    res = get_buffer(conf)
    conf["log"]["clear"]()
    conf["log"]["title"]("SUBSITUTE")
    t = Table(title="Changes")
    t.add_column("Before")
    t.add_column("After")
    for x in res:
        tmp = x.description
        x.description = sub(before_regex, after_regex, tmp)
        t.add_row(easy_lex(tmp), easy_lex(x.description))
    conf["log"]["figure"](t)
    return True

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
        "description": "Defines the core commands",
        "imports": [],
        "lib": {},
        "help": {
            "usage": ("If you are reading this, you are already using this"
                      " plugin")
        }
    }

    commands = {
        "lv": print_buffer_cmd,
        "e!": raw_add_cmd,
        "e": add_cmd,
        "ex": edit_external_cmd,
        "b": block_add_cmd,
        "nop": nop_cmd,
        "ic": command_info_cmd,
        "io": macro_info_cmd,
        "ih": hooks_info_cmd,
        "a": archive_cmd,
        "A": unarchive_cmd,
        "v": select_cmd,
        "V": select_archive_cmd,
        "v!": advanced_select_cmd,
        "l": list_cmd,
        "u": undo_cmd,
        "s": substitute_cmd,
        "ip": projects_info_cmd,
        "ix": context_info_cmd,
        "vv": sub_select_cmd,
        "it": tag_info_cmd
    }

    config = {
        'plugins': {"core": plugin_data},
        'commands': commands,
        'default_command': nop_cmd,
        'null_command': add_cmd,
    }

    return config
