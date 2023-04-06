"""
This module is a directory of internal plugins.
"""

from breadcrumbs.display_plugin import load_plugin as display
from breadcrumbs.util_plugin import load_plugin as util

# The directory
directory = {
    'display': display,
    'core': util
}

