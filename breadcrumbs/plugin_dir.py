"""
This module is a directory of internal plugins.
"""

from breadcrumbs.display_plugin import load_plugin as display
from breadcrumbs.util_plugin import load_plugin as util
from breadcrumbs.future_plugin import load_plugin as future
from breadcrumbs.matrics_plugin import load_plugin as metrics
from breadcrumbs.default_macros_plugin import load_plugin as default_macros

# The directory
directory = {
    'display': display,
    'core': util,
    'future': future,
    'metrics': metrics,
    'default_macros': default_macros
}

