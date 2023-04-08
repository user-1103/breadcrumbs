"""
Defines a some fun addins in a plugin for the breadcrumbs system.
"""
from itertools import filterfalse
from typing import Dict, Any, Union
import holidays

from pytodotxt import Task, TodoTxt
from holidays import USA
from random import randint, shuffle
from randfacts import get_fact
from cowsay import chars, get_output_string
from rich.text import Text
from text2emotion import get_emotion
from better_profanity import profanity
from time import time
from rich._emoji_codes import EMOJI
from deep_translator import MyMemoryTranslator

from breadcrumbs.utils import add_task
from breadcrumbs.metrics_plugin import run_total

# List of us holidays TODO make this more international
holidays = USA()
# List of fellas to say stuff
fellas = list(chars.keys())
# The translator object.
trans: Union[MyMemoryTranslator, None] = None

def init_translator_hook(conf: Dict[str, Any], loaf: TodoTxt) -> None:
    """
    Sets up the translator used by lang_learn.
    """
    global trans
    start_lang = conf['plugins']['fun']['lib']['home_lang']
    end_lang = conf['plugins']['fun']['lib']['guest_lang']
    trans = MyMemoryTranslator(source=start_lang, target=end_lang)

def silly_toast_hook(conf: Dict[str, Any], loaf: TodoTxt) -> None:
    """
    Makes a silly toast. Sometimes.
    """
    silly_toast(conf, loaf)

def lang_learn(conf: Dict[str, Any], loaf: TodoTxt, last_crumb: Task) -> None:
    """
    Learn a language in your own words.

    :param conf: The final conf.
    :param loaf: The loaf.
    :param last_crumb: The last crumb.
    """
    tmp = trans.translate(text=last_crumb.bare_description())
    conf['log']['info'](f"{tmp} :globe_showing_europe-africa:.")


def swear_jar(conf: Dict[str, Any], loaf: TodoTxt, last_crumb_str: str) -> None:
    """
    Tracks your swears.

    :param conf: The final conf.
    :param loaf: The loaf.
    :param last_crumb_str: A string of the last crumb.
    """
    if ("swear_jar" in last_crumb_str):
        return
    crumb_split = last_crumb_str.split()
    swear_vector = [profanity.contains_profanity(x) for x in crumb_split]
    swears = [x for x, y in zip(crumb_split, swear_vector) if (y)]
    for x in swears:
        add_task(loaf, f"swear_jar:1/{x}")
    if (swears):
        conf['log']['info'](f"Added ${len(swears)}.00"
                        f" swear jar"
                        f" :face_with_symbols_on_mouth: :dollar:.")

def party_indicator(conf: Dict[str, Any], loaf: TodoTxt, last_crumb: Task) -> None:
    """
    Is it time to loose your shit?

    :param conf: The final conf.
    :param loaf: The loaf.
    :param last_crumb: The last crumb.
    """
    tmp = holidays.get(last_crumb.creation_date)
    conf['log']['info'](f"Happy {tmp} :party_popper:.")
    do_holiday = False

def is_nice(conf: Dict[str, Any], loaf: TodoTxt, last_crumb_str: str) -> None:
    """
    Very cool. Very cool.

    :param conf: The final conf.
    :param loaf: The loaf.
    :param last_crumb_str: A string of the last crumb.
    """
    if ("420" in last_crumb_str):
        conf['log']['info'](f"Nice :fire:.")
    if ("69" in last_crumb_str):
        conf['log']['info'](f"Nice :wink:.")
    if ("628" in last_crumb_str):
        conf['log']['info'](f"What a horrible animal :cat2:.")
    if ("42 " in last_crumb_str):
        conf['log']['info'](f"It is a mistake to think you can solve any major problems"
                             "just with potatoes. :sweet_potato:.")

def wise_words_of_the_past(conf: Dict[str, Any], loaf: TodoTxt, last_crumb: Task) -> None:
    """
    Words from the smarter, older you.

    :param conf: The final conf.
    :param loaf: The loaf.
    :param last_crumb: The last crumb.
    """
    h = len(loaf.tasks)
    tmp = loaf.tasks[randint(0, h)].bare_description()
    tmp += "\n -- You"
    shuffle(fellas)
    msg = get_output_string(fellas[0], tmp)
    fig = Text.from_ansi(msg, overflow="crop", no_wrap=True, justify="left")
    conf['log']['figure'](fig)

def facts_and_logic(conf: Dict[str, Any], loaf: TodoTxt, last_crumb_str: str) -> None:
    """
    Facts straight from the cows mouth.

    :param conf: The final conf.
    :param loaf: The loaf.
    :param last_crumb_str: A string of the last crumb.
    """
    tmp = get_fact(filter_enabled=False)
    tmp_list = tmp.split()
    do_print = False
    for x in tmp_list:
        if ((x in last_crumb_str) and (len(x) > 2)):
            do_print = True
    if (do_print):
        shuffle(fellas)
        msg = get_output_string(fellas[0], tmp)
        fig = Text.from_ansi(msg, overflow="crop", no_wrap=True, justify="left")
        conf['log']['figure'](fig)

def auto_emote(conf: Dict[str, Any], loaf: TodoTxt, last_crumb_str: str) -> None:
    """
    The emoji movie wasn't that bad. (yes it was).

    :param conf: The final conf.
    :param loaf: The loaf.
    :param last_crumb_str: A string of the last crumb.
    """
    ret = list()
    for k, v in EMOJI.items():
        if (k.split("_")[0] in last_crumb_str):
            ret.append(f":{k}:")
    if (ret):
        shuffle(ret)
        conf['log']['info'](ret[0])

def silly_toast_cmd(conf: Dict[str, Any], loaf: TodoTxt, args: str) -> bool:
    """
    - No args.
    - Tests The silly toasts.
    - Never saves.
    """
    last_crumb = loaf.tasks[-1]
    last_crumb_str = str(last_crumb)
    is_nice(conf, loaf, last_crumb_str)
    if (profanity.contains_profanity(last_crumb_str)):
        swear_jar(conf, loaf, last_crumb_str)
    if ((last_crumb.creation_date in holidays)):
        party_indicator(conf, loaf, last_crumb)
    facts_and_logic(conf, loaf, last_crumb_str)
    wise_words_of_the_past(conf, loaf, last_crumb)
    auto_emote(conf, loaf, last_crumb_str)
    lang_learn(conf, loaf, last_crumb)
    return False

def silly_toast(conf: Dict[str, Any], loaf: TodoTxt) -> None:
    """
    Checks to see if the last message was silly enough to give a silly little toast.

    :param conf: The final conf.
    :param loaf: The loaf.
    """
    ret = time()
    last_crumb = loaf.tasks[-1]
    last_crumb_str = str(last_crumb)
    is_nice(conf, loaf, last_crumb_str)
    if (profanity.contains_profanity(last_crumb)):
        swear_jar(conf, loaf, last_crumb_str)
    if ((not randint(0, 40)) and (last_crumb.creation_date in holidays)):
        party_indicator(conf, loaf, last_crumb)
    if (not randint(0, 10)):
        facts_and_logic(conf, loaf, last_crumb_str)
    if (not randint(0, 10)):
        auto_emote(conf, loaf, last_crumb_str)
    if (not randint(0, 100)):
        wise_words_of_the_past(conf, loaf, last_crumb)
    if (not randint(0, 10)):
        lang_learn(conf, loaf, last_crumb)

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
        "description": "A plugin of shenanigans.",
        "imports": [],
        "lib": {
            "home_lang": 'en',
            "guest_lang": 'es',
        },
        "help": {
            "usage": ("If you are reading this, you are already using this"
                      " plugin")
        }
    }

    hooks = {
        "INIT": [init_translator_hook],
        "MOTD": [],
        "PREMACRO": [],
        "PRECMD": [],
        "CMDERR": [],
        "CMDOK": [silly_toast_hook],
        "POSTCMD": [],
        "EXIT": [],
        "SAFEEXIT": [],
        "FATALEXIT": [],
        "PRINTCRUMB": [],
        "PRINTFIGURE": [],
        "PRINTFIGURE": [],
    }

    commands = {
        "ghoti": silly_toast_cmd
    }

    config = {
        'plugins': {
            "fun": plugin_data,
            "metrics": {
                "lib": {
                    "metrics": [
                        (run_total, "swear_jar", {}, False)
                    ]
                    }
                }
        },
        "hooks": hooks,
        'commands': commands,
    }

    return config




