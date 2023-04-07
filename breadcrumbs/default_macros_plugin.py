"""
Defines the default macros in a plugin for the breadcrumbs system.

The current bastard plugin.
"""
from typing import Dict, Any

from breadcrumbs.matrics_plugin import run_total, span, total_table

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
        "description": "Default macros.",
        "imports": [],
        "lib": {},
        "help": {
            "usage": ("If you are reading this, you are already using this"
                      " plugin")
        }
    }

    macros = {
        # Actual defaults
        ",, to /": (r',,', r'/'),
        "Easy Value Metric": (r'\.\.n\s(\S*)', r'\1:1'),
        # Should be in another plugin
        "Easy Future": (r'\.\.f\s(\S*)', r'FUTURE:\1'),
        # Not actual defaults
        "Easy Cost Metric": (r'\.\.c\s(\S*)\s(\S*)', r'cost:\1/\2'),
        "Easy Track Metric": (r'\.\.t\s(\S*)', r'track:\1'),
        "Easy Mood Metric": (r'\.\.m\s(\S*)', r'mood:\1'),
    }

    config = {
        'plugins': {
            "default_macros": plugin_data,
            'metrics': {
                'lib': {
                    'metrics': [
                        (span,        "track",        {},         True),
                        (span,        "mood",         {},         True),
                        (run_total,   "cost",         {},         True),
                        (total_table, "brush",        {},         True),
                        (total_table, "floss",        {},         True),
                        (total_table, "mwash",        {},         True),
                        (total_table, "shavef",       {},         True),
                        (total_table, "shaveb",       {},         True),
                        (total_table, "showere",      {},         True),
                        (total_table, "showern",      {},         True),
                        (total_table, "vit",          {},         True),
                        (total_table, "zol",          {},         True),
                        (total_table, "thy",          {},         True),
                        (total_table, "laundry",      {},         True),
                        (total_table, "sclean",       {},         True),
                        (total_table, "fclean",       {},         True),
                        (total_table, "exe",          {},         True),
                        (total_table, "str",          {},         True),
                        (total_table, "wake",         {},         True),
                        (total_table, "meal",         {},         True),
                        (total_table, "sleep",        {},         True)

                    ]
                }
            }
        },
        'macros': macros
    }

    return config




